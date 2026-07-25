# Robust .latexmkrc — auto-detects engine, builds to out/, copies PDF back to source.
# Works with: pdflatex, xelatex, lualatex; terminal latexmk; VS Code LaTeX Workshop (with -cd).
# Canonical source: Task-Management/templates/latexmkrc/.latexmkrc
$out_dir = 'out';

# Engine commands (latexmk picks one based on $pdf_mode below)
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';
$xelatex  = 'xelatex  -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';
$lualatex = 'lualatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';

# Auto-detect: lualatex if luacode/lua-ul/luamplib, xelatex if fontspec, else pdflatex.
sub detect_engine {
    my ($file, $seen) = @_;
    $seen //= {};
    return 0 if $seen->{$file}++;
    my $fp = -e $file ? $file : -e "$file.tex" ? "$file.tex" : return 0;
    open(my $fh, '<', $fp) or return 0;
    my $dir = $fp =~ s|/[^/]*$||r; $dir = '.' if $dir eq $fp;
    my $found = 0;
    while (<$fh>) {
        if (/\\usepackage(?:\[[^\]]*\])?\{(?:luacode|lua-ul|luamplib)\}/) { $found = 4; last; }
        if (/\\usepackage(?:\[[^\]]*\])?\{fontspec\}/ && !$found)         { $found = 5; }
        if (/\\(?:input|include)\{([^}]+)\}/) {
            my $sub = $1; $sub = "$dir/$sub" unless $sub =~ m|^/|;
            my $r = detect_engine($sub, $seen);
            if ($r == 4) { $found = 4; last; }
            $found = $r if $r && !$found;
        }
    }
    close($fh);
    return $found;
}

# With no filename on the command line latexmk falls back to @default_files,
# whose own default is ('*.tex') — so a bare `latexmk` tries to typeset every
# .tex in the directory, including preamble fragments and \input children that
# are not documents at all. Restrict it to real drivers: files containing
# \documentclass. Derived, never hardcoded to main.tex — 60 of 269 drivers
# across this estate are named otherwise (venue kits especially).
# A driver needs BOTH \documentclass and \begin{document}. \documentclass alone
# is not enough: shared preamble fragments (e.g. biblatex-preamble.tex, meant to
# be \input) declare a class so editors can lint them, but have no document body
# and must never be typeset on their own.
{
    my @drivers;
    foreach my $f (glob('*.tex')) {
        open(my $fh, '<', $f) or next;
        my ($has_class, $has_body) = (0, 0);
        while (<$fh>) {
            $has_class = 1 if /^\s*\\documentclass/;
            $has_body  = 1 if /\\begin\{document\}/;
            last if $has_class && $has_body;
        }
        close($fh);
        push @drivers, $f if $has_class && $has_body;
    }
    @default_files = @drivers if @drivers;
}

$pdf_mode = 1;  # default: pdflatex
# Detect from the files named on the command line; when none were given, fall
# back to the drivers resolved above, so a bare `latexmk` still selects the
# right engine instead of silently staying on pdflatex.
my @detect_targets = grep { /\.tex$/ } @ARGV;
@detect_targets = @default_files unless @detect_targets;
foreach my $file (@detect_targets) {
    my $m = detect_engine($file);
    if ($m) { $pdf_mode = $m; last; }
}

# Copy compiled PDF back to source directory
END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }
