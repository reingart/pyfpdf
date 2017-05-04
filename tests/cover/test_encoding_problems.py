# -*- coding: utf-8 -*-

"test to visualize encoding problems"

from __future__ import with_statement

#PyFPDF-cover-test:format=PDF
#PyFPDF-cover-test:fn=testoutput.pdf
#PyFPDF-cover-test:hash=e3c74fe7738fba7eed0cd489c597dc88

#
# Please note: with current PyFPDF state four codepoints:
# breve, dotaccent, hungarumlaut and ogonek will not shown in Helveltica.
# 

import common # test utilities
from fpdf import FPDF

import sys
import os, os.path

if common.PY3K:
    unichr = chr

# PDF 1.7/ISO 32000 (PDF 32000-1:2008), Annex D.1, pages 651-672
# Table D.2 Latin Character Set and Encodings (pages 653-656):
# StandardEncoding (STD); MacRomanEncoding (MAC); WinAnsiEncoding (WIN); PDFDocEncoding (PDF)
# csv-style text: 
# Name;Char;STD;MAC;WIN;PDF
# (the last four are octal char code)
# blank lines (;;;;;) are page separator according to the original pages
all_pdf_chars = u""" 
A;A;101;101;101;101
AE;Æ;341;256;306;306
Aacute;Á;-;347;301;301
Acircumflex;Â;-;345;302;302
Adieresis;Ä;-;200;304;304
Agrave;À;-;313;300;300
Aring;Å;-;201;305;305
Atilde;Ã;-;314;303;303
B;B;102;102;102;102
C;C;103;103;103;103
Ccedilla;Ç;-;202;307;307
D;D;104;104;104;104
E;E;105;105;105;105
Eacute;É;-;203;311;311
Ecircumflex;Ê;-;346;312;312
Edieresis;Ë;-;350;313;313
Egrave;È;-;351;310;310
Eth;Ð;-;-;320;320
Euro 1;€;-;-;200;240
F;F;106;106;106;106
G;G;107;107;107;107
H;H;110;110;110;110
I;I;111;111;111;111
Iacute;Í;-;352;315;315
Icircumflex;Î;-;353;316;316
Idieresis;Ï;-;354;317;317
Igrave;Ì;-;355;314;314
J;J;112;112;112;112
K;K;113;113;113;113
L;L;114;114;114;114
Lslash;Ł;350;-;-;225
M;M;115;115;115;115
N;N;116;116;116;116
Ntilde;Ñ;-;204;321;321
O;O;117;117;117;117
;;;;;
OE;Œ;352;316;214;226
Oacute;Ó;-;356;323;323
Ocircumflex;Ô;-;357;324;324
Odieresis;Ö;-;205;326;326
Ograve;Ò;-;361;322;322
Oslash;Ø;351;257;330;330
Otilde;Õ;-;315;325;325
P;P;120;120;120;120
Q;Q;121;121;121;121
R;R;122;122;122;122
S;S;123;123;123;123
Scaron;Š;-;-;212;227
T;T;124;124;124;124
Thorn;Þ;-;-;336;336
U;U;125;125;125;125
Uacute;Ú;-;362;332;332
Ucircumflex;Û;-;363;333;333
Udieresis;Ü;-;206;334;334
Ugrave;Ù;-;364;331;331
V;V;126;126;126;126
W;W;127;127;127;127
X;X;130;130;130;130
Y;Y;131;131;131;131
Yacute;Ý;-;-;335;335
Ydieresis;Ÿ;-;331;237;230
Z;Z;132;132;132;132
Zcaron 2;Ž;-;-;216;231
a;a;141;141;141;141
aacute;á;-;207;341;341
acircumflex;â;-;211;342;342
acute;´;302;253;264;264
adieresis;ä;-;212;344;344
ae;æ;361;276;346;346
agrave;à;-;210;340;340
ampersand;&;46;46;46;46
;;;;;
aring;å;-;214;345;345
asciicircum;^;136;136;136;136
asciitilde;~;176;176;176;176
asterisk;*;52;52;52;52
at;@;100;100;100;100
atilde;ã;-;213;343;343
b;b;142;142;142;142
backslash;\;134;134;134;134
bar;|;174;174;174;174
braceleft;{;173;173;173;173
braceright;};175;175;175;175
bracketleft;[;133;133;133;133
bracketright;];135;135;135;135
breve;˘;306;371;-;30
brokenbar;¦;-;-;246;246
bullet 3;•;267;245;225;200
c;c;143;143;143;143
caron;ˇ;317;377;-;31
ccedilla;ç;-;215;347;347
cedilla;¸;313;374;270;270
cent;¢;242;242;242;242
circumflex;ˆ;303;366;210;32
colon;:;72;72;72;72
comma;,;54;54;54;54
copyright;©;-;251;251;251
currency 1;¤;250;333;244;244
d;d;144;144;144;144
dagger;†;262;240;206;201
daggerdbl;‡;263;340;207;202
degree;°;-;241;260;260
dieresis;¨;310;254;250;250
divide;÷;-;326;367;367
dollar;$;44;44;44;44
dotaccent;˙;307;372;-;33
dotlessi;ı;365;365;-;232
e;e;145;145;145;145
eacute;é;-;216;351;351
;;;;;
ecircumflex;ê;-;220;352;352
edieresis;ë;-;221;353;353
egrave;è;-;217;350;350
eight;8;70;70;70;70
ellipsis;…;274;311;205;203
emdash;—;320;321;227;204
endash;–;261;320;226;205
equal;=;75;75;75;75
eth;ð;-;-;360;360
exclam;!;41;41;41;41
exclamdown;¡;241;301;241;241
f;f;146;146;146;146
fi;ﬁ;256;336;-;223
five;5;65;65;65;65
fl;ﬂ;257;337;-;224
florin;ƒ;246;304;203;206
four;4;64;64;64;64
fraction;⁄;244;332;-;207
g;g;147;147;147;147
germandbls;ß;373;247;337;337
grave;`;301;140;140;140
greater;>;76;76;76;76
guillemotleft 4;«;253;307;253;253
guillemotright 4;»;273;310;273;273
guilsinglleft;‹;254;334;213;210
guilsinglright;›;255;335;233;211
h;h;150;150;150;150
hungarumlaut;˝;315;375;-;34
hyphen 5;-;55;55;55;55
i;i;151;151;151;151
iacute;í;-;222;355;355
icircumflex;î;-;224;356;356
idieresis;ï;-;225;357;357
igrave;ì;-;223;354;354
j;j;152;152;152;152
k;k;153;153;153;153
l;l;154;154;154;154
;;;;;
less;<;74;74;74;74
logicalnot;¬;-;302;254;254
lslash;ł;370;-;-;233
m;m;155;155;155;155
macron;¯;305;370;257;257
minus;−;-;-;-;212
mu;μ;-;265;265;265
multiply;×;-;-;327;327
n;n;156;156;156;156
nine;9;71;71;71;71
ntilde;ñ;-;226;361;361
numbersign;#;43;43;43;43
o;o;157;157;157;157
oacute;ó;-;227;363;363
ocircumflex;ô;-;231;364;364
odieresis;ö;-;232;366;366
oe;œ;372;317;234;234
ogonek;˛;316;376;-;35
ograve;ò;-;230;362;362
one;1;61;61;61;61
onehalf;½;-;-;275;275
onequarter;¼;-;-;274;274
onesuperior;¹;-;-;271;271
ordfeminine;ª;343;273;252;252
ordmasculine;º;353;274;272;272
oslash;ø;371;277;370;370
otilde;õ;-;233;365;365
p;p;160;160;160;160
paragraph;¶;266;246;266;266
parenleft;(;50;50;50;50
parenright;);51;51;51;51
percent;%;45;45;45;45
period;.;56;56;56;56
periodcentered;·;264;341;267;267
perthousand;‰;275;344;211;213
plus;+;53;53;53;53
plusminus;±;-;261;261;261
;;;;;
q;q;161;161;161;161
question;?;77;77;77;77
questiondown;¿;277;300;277;277
quotedbl;";42;42;42;42
quotedblbase;„;271;343;204;214
quotedblleft;“;252;322;223;215
quotedblright;”;272;323;224;216
quoteleft;‘;140;324;221;217
quoteright;’;47;325;222;220
quotesinglbase;‚;270;342;202;221
quotesingle;';251;47;47;47
r;r;162;162;162;162
registered;®;-;250;256;256
ring;˚;312;373;-;36
s;s;163;163;163;163
scaron;š;-;-;232;235
section;§;247;244;247;247
semicolon;";";73;73;73;73
seven;7;67;67;67;67
six;6;66;66;66;66
slash;/;57;57;57;57
space 6;;40;40;40;40
sterling;£;243;243;243;243
t;t;164;164;164;164
thorn;þ;-;-;376;376
three;3;63;63;63;63
threequarters;¾;-;-;276;276
threesuperior;³;-;-;263;263
tilde;˜;304;367;230;37
trademark;™;-;252;231;222
two;2;62;62;62;62
twosuperior;²;-;-;262;262
u;u;165;165;165;165
uacute;ú;-;234;372;372
ucircumflex;û;-;236;373;373
udieresis;ü;-;237;374;374
ugrave;ù;-;235;371;371
;;;;;
underscore;_;137;137;137;137
v;v;166;166;166;166
w;w;167;167;167;167
x;x;170;170;170;170
y;y;171;171;171;171
yacute;ý;-;-;375;375
ydieresis;ÿ;-;330;377;377
yen;¥;245;264;245;245
z;z;172;172;172;172
zcaron 2;ž;-;-;236;236
zero;0;60;60;60;60
"""

windows_1252_chars = u"""
A;A;101;101;101;101
AE;Æ;341;256;306;306
Aacute;Á;-;347;301;301
Acircumflex;Â;-;345;302;302
Adieresis;Ä;-;200;304;304
Agrave;À;-;313;300;300
Aring;Å;-;201;305;305
Atilde;Ã;-;314;303;303
B;B;102;102;102;102
C;C;103;103;103;103
Ccedilla;Ç;-;202;307;307
D;D;104;104;104;104
E;E;105;105;105;105
Eacute;É;-;203;311;311
Ecircumflex;Ê;-;346;312;312
Edieresis;Ë;-;350;313;313
Egrave;È;-;351;310;310
Eth;Ð;-;-;320;320
Euro 1;€;-;-;200;240
F;F;106;106;106;106
G;G;107;107;107;107
H;H;110;110;110;110
I;I;111;111;111;111
Iacute;Í;-;352;315;315
Icircumflex;Î;-;353;316;316
Idieresis;Ï;-;354;317;317
Igrave;Ì;-;355;314;314
J;J;112;112;112;112
K;K;113;113;113;113
L;L;114;114;114;114
M;M;115;115;115;115
N;N;116;116;116;116
Ntilde;Ñ;-;204;321;321
O;O;117;117;117;117
;;;;;
OE;Œ;352;316;214;226
Oacute;Ó;-;356;323;323
Ocircumflex;Ô;-;357;324;324
Odieresis;Ö;-;205;326;326
Ograve;Ò;-;361;322;322
Oslash;Ø;351;257;330;330
Otilde;Õ;-;315;325;325
P;P;120;120;120;120
Q;Q;121;121;121;121
R;R;122;122;122;122
S;S;123;123;123;123
Scaron;Š;-;-;212;227
T;T;124;124;124;124
Thorn;Þ;-;-;336;336
U;U;125;125;125;125
Uacute;Ú;-;362;332;332
Ucircumflex;Û;-;363;333;333
Udieresis;Ü;-;206;334;334
Ugrave;Ù;-;364;331;331
V;V;126;126;126;126
W;W;127;127;127;127
X;X;130;130;130;130
Y;Y;131;131;131;131
Yacute;Ý;-;-;335;335
Ydieresis;Ÿ;-;331;237;230
Z;Z;132;132;132;132
Zcaron 2;Ž;-;-;216;231
a;a;141;141;141;141
aacute;á;-;207;341;341
acircumflex;â;-;211;342;342
acute;´;302;253;264;264
adieresis;ä;-;212;344;344
ae;æ;361;276;346;346
agrave;à;-;210;340;340
ampersand;&;46;46;46;46
;;;;;
aring;å;-;214;345;345
asciicircum;^;136;136;136;136
asciitilde;~;176;176;176;176
asterisk;*;52;52;52;52
at;@;100;100;100;100
atilde;ã;-;213;343;343
b;b;142;142;142;142
backslash;\;134;134;134;134
bar;|;174;174;174;174
braceleft;{;173;173;173;173
braceright;};175;175;175;175
bracketleft;[;133;133;133;133
bracketright;];135;135;135;135
brokenbar;¦;-;-;246;246
bullet 3;•;267;245;225;200
c;c;143;143;143;143
ccedilla;ç;-;215;347;347
cedilla;¸;313;374;270;270
cent;¢;242;242;242;242
circumflex;ˆ;303;366;210;32
colon;:;72;72;72;72
comma;,;54;54;54;54
copyright;©;-;251;251;251
currency 1;¤;250;333;244;244
d;d;144;144;144;144
dagger;†;262;240;206;201
daggerdbl;‡;263;340;207;202
degree;°;-;241;260;260
dieresis;¨;310;254;250;250
divide;÷;-;326;367;367
dollar;$;44;44;44;44
e;e;145;145;145;145
eacute;é;-;216;351;351
;;;;;
ecircumflex;ê;-;220;352;352
edieresis;ë;-;221;353;353
egrave;è;-;217;350;350
eight;8;70;70;70;70
ellipsis;…;274;311;205;203
emdash;—;320;321;227;204
endash;–;261;320;226;205
equal;=;75;75;75;75
eth;ð;-;-;360;360
exclam;!;41;41;41;41
exclamdown;¡;241;301;241;241
f;f;146;146;146;146
five;5;65;65;65;65
florin;ƒ;246;304;203;206
four;4;64;64;64;64
g;g;147;147;147;147
germandbls;ß;373;247;337;337
grave;`;301;140;140;140
greater;>;76;76;76;76
guillemotleft 4;«;253;307;253;253
guillemotright 4;»;273;310;273;273
guilsinglleft;‹;254;334;213;210
guilsinglright;›;255;335;233;211
h;h;150;150;150;150
hyphen 5;-;55;55;55;55
i;i;151;151;151;151
iacute;í;-;222;355;355
icircumflex;î;-;224;356;356
idieresis;ï;-;225;357;357
igrave;ì;-;223;354;354
j;j;152;152;152;152
k;k;153;153;153;153
l;l;154;154;154;154
;;;;;
less;<;74;74;74;74
logicalnot;¬;-;302;254;254
m;m;155;155;155;155
macron;¯;305;370;257;257
multiply;×;-;-;327;327
n;n;156;156;156;156
nine;9;71;71;71;71
ntilde;ñ;-;226;361;361
numbersign;#;43;43;43;43
o;o;157;157;157;157
oacute;ó;-;227;363;363
ocircumflex;ô;-;231;364;364
odieresis;ö;-;232;366;366
oe;œ;372;317;234;234
ograve;ò;-;230;362;362
one;1;61;61;61;61
onehalf;½;-;-;275;275
onequarter;¼;-;-;274;274
onesuperior;¹;-;-;271;271
ordfeminine;ª;343;273;252;252
ordmasculine;º;353;274;272;272
oslash;ø;371;277;370;370
otilde;õ;-;233;365;365
p;p;160;160;160;160
paragraph;¶;266;246;266;266
parenleft;(;50;50;50;50
parenright;);51;51;51;51
percent;%;45;45;45;45
period;.;56;56;56;56
periodcentered;·;264;341;267;267
perthousand;‰;275;344;211;213
plus;+;53;53;53;53
plusminus;±;-;261;261;261
;;;;;
q;q;161;161;161;161
question;?;77;77;77;77
questiondown;¿;277;300;277;277
quotedbl;";42;42;42;42
quotedblbase;„;271;343;204;214
quotedblleft;“;252;322;223;215
quotedblright;”;272;323;224;216
quoteleft;‘;140;324;221;217
quoteright;’;47;325;222;220
quotesinglbase;‚;270;342;202;221
quotesingle;';251;47;47;47
r;r;162;162;162;162
registered;®;-;250;256;256
s;s;163;163;163;163
scaron;š;-;-;232;235
section;§;247;244;247;247
semicolon;";";73;73;73;73
seven;7;67;67;67;67
six;6;66;66;66;66
slash;/;57;57;57;57
space 6;;40;40;40;40
sterling;£;243;243;243;243
t;t;164;164;164;164
thorn;þ;-;-;376;376
three;3;63;63;63;63
threequarters;¾;-;-;276;276
threesuperior;³;-;-;263;263
tilde;˜;304;367;230;37
trademark;™;-;252;231;222
two;2;62;62;62;62
twosuperior;²;-;-;262;262
u;u;165;165;165;165
uacute;ú;-;234;372;372
ucircumflex;û;-;236;373;373
udieresis;ü;-;237;374;374
ugrave;ù;-;235;371;371
;;;;;
underscore;_;137;137;137;137
v;v;166;166;166;166
w;w;167;167;167;167
x;x;170;170;170;170
y;y;171;171;171;171
yacute;ý;-;-;375;375
ydieresis;ÿ;-;330;377;377
yen;¥;245;264;245;245
z;z;172;172;172;172
zcaron 2;ž;-;-;236;236
zero;0;60;60;60;60
"""

chars_not_in_windows_1252 = u"""
Lslash;Ł;350;-;-;225
breve;˘;306;371;-;30
caron;ˇ;317;377;-;31
dotaccent;˙;307;372;-;33
dotlessi;ı;365;365;-;232
fi;ﬁ;256;336;-;223
fl;ﬂ;257;337;-;224
fraction;⁄;244;332;-;207
hungarumlaut;˝;315;375;-;34
lslash;ł;370;-;-;233
minus;−;-;-;-;212
mu;μ;-;265;265;265
ogonek;˛;316;376;-;35
ring;˚;312;373;-;36
"""

latin_1_chars = u"""
A;A;101;101;101;101
AE;Æ;341;256;306;306
Aacute;Á;-;347;301;301
Acircumflex;Â;-;345;302;302
Adieresis;Ä;-;200;304;304
Agrave;À;-;313;300;300
Aring;Å;-;201;305;305
Atilde;Ã;-;314;303;303
B;B;102;102;102;102
C;C;103;103;103;103
Ccedilla;Ç;-;202;307;307
D;D;104;104;104;104
E;E;105;105;105;105
Eacute;É;-;203;311;311
Ecircumflex;Ê;-;346;312;312
Edieresis;Ë;-;350;313;313
Egrave;È;-;351;310;310
Eth;Ð;-;-;320;320
F;F;106;106;106;106
G;G;107;107;107;107
H;H;110;110;110;110
I;I;111;111;111;111
Iacute;Í;-;352;315;315
Icircumflex;Î;-;353;316;316
Idieresis;Ï;-;354;317;317
Igrave;Ì;-;355;314;314
J;J;112;112;112;112
K;K;113;113;113;113
L;L;114;114;114;114
M;M;115;115;115;115
N;N;116;116;116;116
Ntilde;Ñ;-;204;321;321
O;O;117;117;117;117
;;;;;
Oacute;Ó;-;356;323;323
Ocircumflex;Ô;-;357;324;324
Odieresis;Ö;-;205;326;326
Ograve;Ò;-;361;322;322
Oslash;Ø;351;257;330;330
Otilde;Õ;-;315;325;325
P;P;120;120;120;120
Q;Q;121;121;121;121
R;R;122;122;122;122
S;S;123;123;123;123
T;T;124;124;124;124
Thorn;Þ;-;-;336;336
U;U;125;125;125;125
Uacute;Ú;-;362;332;332
Ucircumflex;Û;-;363;333;333
Udieresis;Ü;-;206;334;334
Ugrave;Ù;-;364;331;331
V;V;126;126;126;126
W;W;127;127;127;127
X;X;130;130;130;130
Y;Y;131;131;131;131
Yacute;Ý;-;-;335;335
Z;Z;132;132;132;132
a;a;141;141;141;141
aacute;á;-;207;341;341
acircumflex;â;-;211;342;342
acute;´;302;253;264;264
adieresis;ä;-;212;344;344
ae;æ;361;276;346;346
agrave;à;-;210;340;340
ampersand;&;46;46;46;46
;;;;;
aring;å;-;214;345;345
asciicircum;^;136;136;136;136
asciitilde;~;176;176;176;176
asterisk;*;52;52;52;52
at;@;100;100;100;100
atilde;ã;-;213;343;343
b;b;142;142;142;142
backslash;\;134;134;134;134
bar;|;174;174;174;174
braceleft;{;173;173;173;173
braceright;};175;175;175;175
bracketleft;[;133;133;133;133
bracketright;];135;135;135;135
brokenbar;¦;-;-;246;246
c;c;143;143;143;143
ccedilla;ç;-;215;347;347
cedilla;¸;313;374;270;270
cent;¢;242;242;242;242
colon;:;72;72;72;72
comma;,;54;54;54;54
copyright;©;-;251;251;251
currency 1;¤;250;333;244;244
d;d;144;144;144;144
degree;°;-;241;260;260
dieresis;¨;310;254;250;250
divide;÷;-;326;367;367
dollar;$;44;44;44;44
e;e;145;145;145;145
eacute;é;-;216;351;351
;;;;;
ecircumflex;ê;-;220;352;352
edieresis;ë;-;221;353;353
egrave;è;-;217;350;350
eight;8;70;70;70;70
equal;=;75;75;75;75
eth;ð;-;-;360;360
exclam;!;41;41;41;41
exclamdown;¡;241;301;241;241
f;f;146;146;146;146
five;5;65;65;65;65
four;4;64;64;64;64
g;g;147;147;147;147
germandbls;ß;373;247;337;337
grave;`;301;140;140;140
greater;>;76;76;76;76
guillemotleft 4;«;253;307;253;253
guillemotright 4;»;273;310;273;273
h;h;150;150;150;150
hyphen 5;-;55;55;55;55
i;i;151;151;151;151
iacute;í;-;222;355;355
icircumflex;î;-;224;356;356
idieresis;ï;-;225;357;357
igrave;ì;-;223;354;354
j;j;152;152;152;152
k;k;153;153;153;153
l;l;154;154;154;154
;;;;;
less;<;74;74;74;74
logicalnot;¬;-;302;254;254
m;m;155;155;155;155
macron;¯;305;370;257;257
multiply;×;-;-;327;327
n;n;156;156;156;156
nine;9;71;71;71;71
ntilde;ñ;-;226;361;361
numbersign;#;43;43;43;43
o;o;157;157;157;157
oacute;ó;-;227;363;363
ocircumflex;ô;-;231;364;364
odieresis;ö;-;232;366;366
ograve;ò;-;230;362;362
one;1;61;61;61;61
onehalf;½;-;-;275;275
onequarter;¼;-;-;274;274
onesuperior;¹;-;-;271;271
ordfeminine;ª;343;273;252;252
ordmasculine;º;353;274;272;272
oslash;ø;371;277;370;370
otilde;õ;-;233;365;365
p;p;160;160;160;160
paragraph;¶;266;246;266;266
parenleft;(;50;50;50;50
parenright;);51;51;51;51
percent;%;45;45;45;45
period;.;56;56;56;56
periodcentered;·;264;341;267;267
plus;+;53;53;53;53
plusminus;±;-;261;261;261
;;;;;
q;q;161;161;161;161
question;?;77;77;77;77
questiondown;¿;277;300;277;277
quotedbl;";42;42;42;42
quotesingle;';251;47;47;47
r;r;162;162;162;162
registered;®;-;250;256;256
s;s;163;163;163;163
section;§;247;244;247;247
semicolon;";";73;73;73;73
seven;7;67;67;67;67
six;6;66;66;66;66
slash;/;57;57;57;57
space 6;;40;40;40;40
sterling;£;243;243;243;243
t;t;164;164;164;164
thorn;þ;-;-;376;376
three;3;63;63;63;63
threequarters;¾;-;-;276;276
threesuperior;³;-;-;263;263
two;2;62;62;62;62
twosuperior;²;-;-;262;262
u;u;165;165;165;165
uacute;ú;-;234;372;372
ucircumflex;û;-;236;373;373
udieresis;ü;-;237;374;374
ugrave;ù;-;235;371;371
;;;;;
underscore;_;137;137;137;137
v;v;166;166;166;166
w;w;167;167;167;167
x;x;170;170;170;170
y;y;171;171;171;171
yacute;ý;-;-;375;375
ydieresis;ÿ;-;330;377;377
yen;¥;245;264;245;245
z;z;172;172;172;172
zero;0;60;60;60;60
"""

# 1. Part) chars_not_in_windows_1252
# 2. Part) additional chars not in latin1
chars_not_in_latin_1 = u"""
Lslash;Ł;350;-;-;225
breve;˘;306;371;-;30
caron;ˇ;317;377;-;31
dotaccent;˙;307;372;-;33
dotlessi;ı;365;365;-;232
fi;ﬁ;256;336;-;223
fl;ﬂ;257;337;-;224
fraction;⁄;244;332;-;207
hungarumlaut;˝;315;375;-;34
lslash;ł;370;-;-;233
minus;−;-;-;-;212
mu;μ;-;265;265;265
ogonek;˛;316;376;-;35
ring;˚;312;373;-;36
;;;;;
emdash;—;320;321;227;204
endash;–;261;320;226;205
Euro 1;€;-;-;200;240
OE;Œ;352;316;214;226
Scaron;Š;-;-;212;227
Ydieresis;Ÿ;-;331;237;230
Zcaron 2;Ž;-;-;216;231
bullet 3;•;267;245;225;200
circumflex;ˆ;303;366;210;32
dagger;†;262;240;206;201
daggerdbl;‡;263;340;207;202
ellipsis;…;274;311;205;203
florin;ƒ;246;304;203;206
guilsinglleft;‹;254;334;213;210
guilsinglright;›;255;335;233;211
oe;œ;372;317;234;234
perthousand;‰;275;344;211;213
quotedblbase;„;271;343;204;214
quotedblleft;“;252;322;223;215
quotedblright;”;272;323;224;216
quoteleft;‘;140;324;221;217
quoteright;’;47;325;222;220
quotesinglbase;‚;270;342;202;221
scaron;š;-;-;232;235
tilde;˜;304;367;230;37
trademark;™;-;252;231;222
zcaron 2;ž;-;-;236;236
"""

@common.add_unittest
def dotest(outputname, nostamp):
    pdf = FPDF()
    pdf.unifontsubset = False
    if nostamp:
        pdf._putinfo = lambda: common.test_putinfo(pdf)
    pdf.add_page()
    pdf.set_font('Arial', 'I', 8)

    # 1. Test:
    # with txt = txt.encode('latin1') in function normalize_text of module fpdf.py
    # and using
    #
    # txt = all_pdf_chars
    #
    # you will get
    #       "UnicodeEncodeError: 'latin-1' codec can't encode character"
    # for each of the chars in chars_not_in_latin_1
    
    # 2. Test:
    # with txt = txt.encode('windows-2') in function normalize_text of module fpdf.py
    # and using
    #
    # txt = all_pdf_chars
    #
    # you will get
    #       "UnicodeEncodeError: 'windows-1252' codec can't encode character"
    # for each of the chars in chars_not_in_windows_1252
    
    # 3. Test
    # with txt = txt.encode('latin1') in function normalize_text of module fpdf.py
    # and using
    #
    # txt = latin_1_chars
    #
    # you don't get these errors

    # 4. Test
    # with txt = txt.encode('windows-1252') in function normalize_text of module fpdf.py
    # and using

    txt = windows_1252_chars
    
    # you either don't get these errors


    # to summarize
    # all_pdf_chars = windows_1252_chars + chars_not_in_windows_1252
    # all_pdf_chars = latin_1_chars + chars_not_in_latin_1
    
    def nrOfChars(var):
        if var in [all_pdf_chars,windows_1252_chars,latin_1_chars]:
            return len(var.split('\n'))-2-6
        elif var == chars_not_in_windows_1252:
            return len(var.split('\n'))-2
        elif var == chars_not_in_latin_1:
            return len(var.split('\n'))-2-1

    chartexts = {'all':all_pdf_chars,
                 'windows-1252':windows_1252_chars,
                 'latin1':latin_1_chars,
                 'not_in_windows_1252':chars_not_in_windows_1252,
                 'not_in_latin_1':chars_not_in_latin_1}
    for k in chartexts.keys():
        print(k,nrOfChars(chartexts[k]))

    # Output:
    #('all', 229)
    #('windows-1252', 215)
    #('latin1', 188)
    #('not_in_windows_1252', 14)
    #('not_in_latin_1', 41)
    # 
    # => not_in_latin_1 - not_in_windows_1252 = 27
    
    pdf.write(8, txt)

    pdf.output(outputname, 'F')

if __name__ == "__main__":
    common.testmain(__file__, dotest)
