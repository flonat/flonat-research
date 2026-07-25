# Engine pinned to xelatex: flonat-wp requires fontspec + unicode-math,
# and arXiv supports xelatex but NOT lualatex (arXiv TeX Live FAQ, Nov 2025).
# Validated 2026-07-25 across 26 papers: 0 regressions, 10 previously-broken fixed.
$out_dir = 'out';
$xelatex = 'xelatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';
$pdf_mode = 5;
END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }