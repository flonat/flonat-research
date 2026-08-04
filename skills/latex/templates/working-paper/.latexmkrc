# Canonical .latexmkrc -- one fail-closed build contract for local LaTeX projects.
# Authoring source: Task-Management/templates/latexmkrc/.latexmkrc
$out_dir = 'out';

# Command-line engine flags are processed after rc files, so an explicit
# -pdflatex, -xelatex, or -lualatex remains authoritative.
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';
$xelatex  = 'xelatex  -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';
$lualatex = 'lualatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';

require Cwd;
require Digest::SHA;
require File::Basename;
require File::Copy;
require File::Spec;

our %flonat_engine_label = (
    1 => 'pdflatex',
    4 => 'lualatex',
    5 => 'xelatex',
);

our %flonat_beamer_theme_prefix = (
    usetheme       => 'beamertheme',
    usecolortheme  => 'beamercolortheme',
    usefonttheme   => 'beamerfonttheme',
    useinnertheme  => 'beamerinnertheme',
    useoutertheme  => 'beameroutertheme',
);

sub flonat_read_text {
    my ($path) = @_;
    open(my $fh, '<', $path) or return undef;
    local $/;
    my $text = <$fh>;
    close($fh);
    return $text;
}

# Remove TeX comments while preserving escaped percent signs. Magic comments
# are read from the raw driver before this function is called.
sub flonat_strip_comments {
    my ($text) = @_;
    my @clean;
    foreach my $line (split(/\n/, $text, -1)) {
        my $cut = length($line);
        for (my $i = 0; $i < length($line); $i++) {
            next unless substr($line, $i, 1) eq '%';
            my $slashes = 0;
            for (my $j = $i - 1; $j >= 0 && substr($line, $j, 1) eq '\\'; $j--) {
                $slashes++;
            }
            if ($slashes % 2 == 0) {
                $cut = $i;
                last;
            }
        }
        push @clean, substr($line, 0, $cut);
    }
    return join("\n", @clean);
}

sub flonat_trim {
    my ($value) = @_;
    $value //= '';
    $value =~ s/^\s+//;
    $value =~ s/\s+$//;
    return $value;
}

# Local classes and packages commonly contain engine-compatibility branches,
# for example acmart's \ifxetex ... \else \ifluatex ... \else pdfTeX ...
# sequence.  Requirements inside those branches describe what to do *after*
# an engine has been chosen; they must not themselves choose that engine.
# Mask complete engine-condition blocks before scanning requirements.  If a
# block cannot be balanced conservatively, leave it visible and fail closed.
sub flonat_mask_engine_conditionals {
    my ($text) = @_;
    my @tokens;
    while ($text =~ /\\([A-Za-z@]+|.)/g) {
        push @tokens, [$1, $-[0], $+[0]];
    }

    my %engine_if = map { $_ => 1 } qw(
        ifxetex ifXeTeX ifluatex ifLuaTeX ifpdftex ifPDFTeX
    );
    my %function_style_if = map { $_ => 1 } qw(
        ifthenelse ifstrequal ifcsstrequal ifdef ifcsdef ifundef ifcsundef
        ifboolexpr ifbool iftoggle ifnumequal ifnumcomp ifdimequal ifdimcomp
        ifblank ifstrempty ifcsstring ifcsequal ifdefstring ifdequal
        ifpatchable iflanguage
    );

    my @ranges;
    for (my $i = 0; $i < @tokens; $i++) {
        my ($name, $start) = @{$tokens[$i]};
        next unless $engine_if{$name};
        next if @ranges && $start < $ranges[-1]->[1];

        my $depth = 0;
        my $end;
        for (my $j = $i; $j < @tokens; $j++) {
            my ($nested, undef, $token_end) = @{$tokens[$j]};
            if ($nested eq 'fi') {
                $depth--;
                if ($depth == 0) {
                    $end = $token_end;
                    last;
                }
                last if $depth < 0;
            }
            elsif (($nested =~ /^if/ && !$function_style_if{$nested})
                || $engine_if{$nested}) {
                $depth++;
            }
        }
        push @ranges, [$start, $end] if defined $end;
    }

    foreach my $range (reverse @ranges) {
        my ($start, $end) = @{$range};
        my $masked = substr($text, $start, $end - $start);
        $masked =~ s/[^\n]/ /g;
        substr($text, $start, $end - $start, $masked);
    }
    return $text;
}

sub flonat_existing_path {
    my ($name, $default_extension, $from_dir, $project_dir) = @_;
    $name = flonat_trim($name);
    return undef if $name eq '' || $name =~ /[\\#]/;

    my @names = ($name);
    push @names, "$name.$default_extension" unless $name =~ /\.[^\/]+$/;
    my @roots = ($from_dir, $project_dir, '.');
    my %seen;
    foreach my $candidate_name (@names) {
        if (File::Spec->file_name_is_absolute($candidate_name)) {
            return Cwd::abs_path($candidate_name) if -f $candidate_name;
            next;
        }
        foreach my $root (@roots) {
            my $candidate = File::Spec->catfile($root, $candidate_name);
            next if $seen{$candidate}++;
            return Cwd::abs_path($candidate) if -f $candidate;
        }
    }
    return undef;
}

sub flonat_record_requirement {
    my ($requirements, $kind, $path, $reason) = @_;
    push @{$requirements->{$kind}}, "$path: $reason";
}

sub flonat_scan_local_file {
    my ($path, $project_dir, $requirements, $seen, $is_driver) = @_;
    my $absolute = Cwd::abs_path($path);
    return unless defined $absolute && -f $absolute;
    return if $seen->{$absolute}++;

    my $raw = flonat_read_text($absolute);
    return unless defined $raw;
    my $from_dir = File::Basename::dirname($absolute);

    if ($is_driver) {
        while ($raw =~ /^\s*%\s*!\s*TEX\s+(?:TS-)?program\s*=\s*(pdf(?:la)?tex|xelatex|lualatex)\b/img) {
            my $program = lc($1);
            my $mode = $program eq 'lualatex' ? 4 : $program eq 'xelatex' ? 5 : 1;
            push @{$requirements->{magic}}, [$mode, "$absolute: % !TEX program = $program"];
        }
    }

    my $clean = flonat_mask_engine_conditionals(flonat_strip_comments($raw));
    flonat_record_requirement($requirements, 'lua', $absolute, 'LuaTeX primitive')
        if $clean =~ /\\(?:directlua|latelua|luafunction|luaescapestring)\b/;
    flonat_record_requirement($requirements, 'xe', $absolute, 'XeTeX primitive')
        if $clean =~ /\\XeTeX\w*/;
    flonat_record_requirement($requirements, 'unicode', $absolute, 'font-selection command')
        if $clean =~ /\\(?:setmainfont|setsansfont|setmonofont|setmathfont)\b/;

    while ($clean =~ /\\(?:usepackage|RequirePackage)\s*(?:\[[^\]]*\]\s*)?\{([^{}]+)\}/sg) {
        foreach my $package (split(/,/, $1)) {
            $package = flonat_trim($package);
            next if $package eq '';
            my $base = lc(File::Basename::basename($package));
            $base =~ s/\.sty$//;
            if ($base =~ /^(?:flonat-beamer|luacode|lua-ul|luamplib|luaotfload|luatexbase|luatexja)$/) {
                flonat_record_requirement($requirements, 'lua', $absolute, "package $package");
            }
            elsif ($base =~ /^(?:xltxtra|xunicode|xecjk|mathspec)$/) {
                flonat_record_requirement($requirements, 'xe', $absolute, "package $package");
            }
            elsif ($base =~ /^(?:fontspec|unicode-math|polyglossia)$/) {
                flonat_record_requirement($requirements, 'unicode', $absolute, "package $package");
            }

            my $local = flonat_existing_path($package, 'sty', $from_dir, $project_dir);
            flonat_scan_local_file($local, $project_dir, $requirements, $seen, 0)
                if defined $local;
        }
    }

    while ($clean =~ /\\(?:documentclass|LoadClass)\s*(?:\[[^\]]*\]\s*)?\{([^{}]+)\}/sg) {
        foreach my $class (split(/,/, $1)) {
            my $local = flonat_existing_path($class, 'cls', $from_dir, $project_dir);
            flonat_scan_local_file($local, $project_dir, $requirements, $seen, 0)
                if defined $local;
        }
    }

    # Beamer's theme commands load packages through generated filenames rather
    # than \\usepackage. Follow local theme files so an engine requirement hidden
    # in (for example) beamerthemegemini.sty remains visible to the driver.
    while ($clean =~ /\\(use(?:color|font|inner|outer)?theme)\s*(?:\[[^\]]*\]\s*)?\{([^{}]+)\}/sg) {
        my ($command, $theme_list) = ($1, $2);
        my $prefix = $flonat_beamer_theme_prefix{$command};
        next unless defined $prefix;
        foreach my $theme (split(/,/, $theme_list)) {
            $theme = flonat_trim($theme);
            next if $theme eq '';
            my $local = flonat_existing_path("$prefix$theme", 'sty', $from_dir, $project_dir);
            flonat_scan_local_file($local, $project_dir, $requirements, $seen, 0)
                if defined $local;
        }
    }

    while ($clean =~ /\\(?:input|include|subfile)\s*\{([^{}]+)\}/sg) {
        my $local = flonat_existing_path($1, 'tex', $from_dir, $project_dir);
        flonat_scan_local_file($local, $project_dir, $requirements, $seen, 0)
            if defined $local;
    }
    while ($clean =~ /\\input\s+([^\s{}%]+)/sg) {
        my $local = flonat_existing_path($1, 'tex', $from_dir, $project_dir);
        flonat_scan_local_file($local, $project_dir, $requirements, $seen, 0)
            if defined $local;
    }
}

sub flonat_first_reason {
    my ($requirements, $kind) = @_;
    return $requirements->{$kind}->[0] // $kind;
}

sub flonat_engine_for_target {
    my ($target) = @_;
    my $absolute = Cwd::abs_path($target);
    die "latexmkrc: cannot inspect TeX target '$target'\n" unless defined $absolute;
    my $project_dir = File::Basename::dirname($absolute);
    my %requirements = (lua => [], xe => [], unicode => [], magic => []);
    my %seen;
    flonat_scan_local_file($absolute, $project_dir, \%requirements, \%seen, 1);

    my %magic_modes;
    foreach my $magic (@{$requirements{magic}}) {
        $magic_modes{$magic->[0]} = $magic->[1];
    }
    if (keys(%magic_modes) > 1) {
        die "latexmkrc: '$target' contains conflicting % !TEX program declarations\n";
    }

    my ($magic_mode) = keys(%magic_modes);
    my $has_lua = @{$requirements{lua}} > 0;
    my $has_xe = @{$requirements{xe}} > 0;
    my $has_unicode = @{$requirements{unicode}} > 0;
    if (defined $magic_mode) {
        if ($magic_mode == 1 && ($has_lua || $has_xe || $has_unicode)) {
            die "latexmkrc: '$target' declares pdflatex but requires a Unicode engine\n";
        }
        if ($magic_mode == 4 && $has_xe) {
            die "latexmkrc: '$target' declares lualatex but requires XeLaTeX (" .
                flonat_first_reason(\%requirements, 'xe') . ")\n";
        }
        if ($magic_mode == 5 && $has_lua) {
            die "latexmkrc: '$target' declares xelatex but requires LuaLaTeX (" .
                flonat_first_reason(\%requirements, 'lua') . ")\n";
        }
        return $magic_mode;
    }

    if ($has_lua && $has_xe) {
        die "latexmkrc: '$target' has conflicting LuaLaTeX and XeLaTeX requirements\n";
    }
    return 4 if $has_lua;
    return 5 if $has_xe || $has_unicode;
    return 1;
}

sub flonat_is_driver {
    my ($path) = @_;
    my $raw = flonat_read_text($path);
    return 0 unless defined $raw;
    my $clean = flonat_strip_comments($raw);
    return $clean =~ /\\documentclass(?:\s*\[[^\]]*\])?\s*\{/s
        && $clean =~ /\\begin\s*\{document\}/s;
}

sub flonat_cli_engine_override {
    foreach my $arg (@ARGV) {
        return 4 if $arg =~ /^--?(?:lualatex|pdflua)$/;
        return 5 if $arg =~ /^--?(?:xelatex|pdfxelatex)$/;
        return 1 if $arg =~ /^--?(?:pdf|pdflatex)$/;
    }
    return undef;
}

sub flonat_cli_targets {
    my @targets;
    my %seen;
    foreach my $arg (@ARGV) {
        next if $arg =~ /^-/;
        my $candidate;
        if ($arg =~ /\.tex$/i && -f $arg) {
            $candidate = $arg;
        }
        elsif (-f "$arg.tex") {
            $candidate = "$arg.tex";
        }
        next unless defined $candidate;
        my $absolute = Cwd::abs_path($candidate) // $candidate;
        push @targets, $candidate unless $seen{$absolute}++;
    }
    return @targets;
}

sub flonat_load_local_supplement {
    my (@targets) = @_;
    my %directories;
    foreach my $target (@targets) {
        my $absolute = Cwd::abs_path($target);
        next unless defined $absolute;
        $directories{File::Basename::dirname($absolute)} = 1;
    }
    $directories{Cwd::getcwd()} = 1 unless %directories;
    return unless keys(%directories) == 1;

    my ($directory) = keys(%directories);
    my $supplement = File::Spec->catfile($directory, '.latexmkrc.local');
    return unless -f $supplement;
    my $result = do $supplement;
    if (!defined $result) {
        my $reason = $@ || $! || 'unknown error';
        die "latexmkrc: cannot load '$supplement': $reason\n";
    }
}

# A bare latexmk must never compile include fragments. An empty driver list is
# intentional: latexmk then exits with its own no-input diagnostic.
my @flonat_drivers = sort grep { flonat_is_driver($_) } glob('*.tex');
@default_files = @flonat_drivers;

our @flonat_requested_targets = flonat_cli_targets();

# Load project-specific paths and bare-build defaults before resolving the
# requested target set. Explicit CLI targets remain authoritative; a local
# @default_files declaration only narrows a bare invocation.
my $flonat_mode_was_defined = defined($pdf_mode);
my $flonat_mode_before_local = $pdf_mode;
flonat_load_local_supplement(@flonat_requested_targets);
if ($flonat_mode_was_defined != defined($pdf_mode)
    || (defined($pdf_mode) && $pdf_mode != $flonat_mode_before_local)) {
    die "latexmkrc: .latexmkrc.local must not set \$pdf_mode; use a driver magic comment or CLI engine flag\n";
}

@flonat_requested_targets = @default_files unless @flonat_requested_targets;
my $flonat_cli_mode = flonat_cli_engine_override();
if (defined $flonat_cli_mode) {
    $pdf_mode = $flonat_cli_mode;
}
else {
    my %flonat_modes;
    my @flonat_descriptions;
    foreach my $target (@flonat_requested_targets) {
        my $mode = flonat_engine_for_target($target);
        $flonat_modes{$mode} = 1;
        push @flonat_descriptions, "$target=$flonat_engine_label{$mode}";
    }
    if (keys(%flonat_modes) > 1) {
        die "latexmkrc: conflicting engine requirements across targets (" .
            join(', ', @flonat_descriptions) .
            "). Build one driver at a time or pass an explicit engine flag.\n";
    }
    my ($flonat_mode) = keys(%flonat_modes);
    $pdf_mode = defined $flonat_mode ? $flonat_mode : 1;
}

sub flonat_sha256 {
    my ($path) = @_;
    open(my $fh, '<:raw', $path)
        or die "cannot open '$path' for hashing: $!";
    my $sha = Digest::SHA->new(256);
    $sha->addfile($fh);
    close($fh)
        or die "cannot close '$path' after hashing: $!";
    return $sha->hexdigest;
}

sub flonat_publish_pdf {
    my ($source, $destination) = @_;

    my $destination_dir = File::Basename::dirname($destination);
    my $destination_name = File::Basename::basename($destination);
    my $temporary = File::Spec->catfile(
        $destination_dir,
        ".$destination_name.tmp.$$"
    );

    my $source_before = flonat_sha256($source);

    eval {
        File::Copy::copy($source, $temporary)
            or die "cannot copy '$source' to '$temporary': $!";

        my $source_after = flonat_sha256($source);
        my $temporary_hash = flonat_sha256($temporary);

        die "source PDF changed during copy: '$source'\n"
            unless $source_before eq $source_after;

        die "temporary PDF does not match source: '$temporary'\n"
            unless $temporary_hash eq $source_after;

        rename($temporary, $destination)
            or die "cannot publish '$temporary' as '$destination': $!";

        my $source_final = flonat_sha256($source);
        my $destination_hash = flonat_sha256($destination);

        die "published PDF does not match source: '$destination'\n"
            unless $destination_hash eq $source_final;
    };

    my $error = $@;
    unlink($temporary) if -e $temporary;
    die $error if $error;
}

# Copy only PDFs belonging to requested targets, only after a successful build.
# Preserve Perl's saved exit status: changing $? in an END block can otherwise
# turn a failed latexmk invocation into exit code 0.
END {
    my $saved_status = $?;
    if ($saved_status == 0
        && defined($failure_count) && $failure_count == 0
        && !(defined($cleanup_only) && $cleanup_only)
        && defined($pdf_mode) && $pdf_mode != 0
        && defined($out_dir) && @file_list) {
        eval {
            my %copied;
            my @copy_targets = @flonat_requested_targets
                ? @flonat_requested_targets
                : @file_list;
            foreach my $tex_target (@copy_targets) {
                my $source_dir = File::Basename::dirname($tex_target);
                my $base = File::Basename::basename($tex_target);
                $base =~ s/\.[^.]+$//;
                if (defined($jobname) && $jobname ne '') {
                    my $named = $jobname;
                    $named =~ s/%A/$base/g;
                    $base = $named;
                }

                my $built_pdf;
                if (File::Spec->file_name_is_absolute($out_dir)) {
                    $built_pdf = File::Spec->catfile($out_dir, "$base.pdf");
                }
                elsif (defined($do_cd) && $do_cd) {
                    $built_pdf = File::Spec->catfile($source_dir, $out_dir, "$base.pdf");
                }
                else {
                    $built_pdf = File::Spec->catfile($out_dir, "$base.pdf");
                }
                die "expected built PDF does not exist: '$built_pdf'\n"
                    unless -f $built_pdf;

                my $destination = File::Spec->catfile($source_dir, "$base.pdf");
                next if $copied{$destination}++;
                flonat_publish_pdf($built_pdf, $destination);
            }
        };
        if ($@) {
            warn "latexmkrc: PDF copy-back failed: $@\n";
            $saved_status = 12;
        }
    }
    $? = $saved_status;
}
