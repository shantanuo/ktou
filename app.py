import re
import zipfile
from io import BytesIO

import streamlit as st
from defusedxml import ElementTree as ET


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Krutidev to Unicode Converter",
    page_icon="📄",
    layout="centered"
)


# ============================================================
# APOSTROPHE NORMALIZATION
# ============================================================

APOSTROPHE_EQUIVALENTS = {
    "\u2019": "'",   # ’ RIGHT SINGLE QUOTATION MARK
    "\u2018": "'",   # ‘ LEFT SINGLE QUOTATION MARK
    "\u02BC": "'",   # ʼ MODIFIER LETTER APOSTROPHE
    "\u201B": "'",   # ‛ SINGLE HIGH-REVERSED-9 QUOTATION MARK
    "\u00B4": "'",   # ´ ACUTE ACCENT
}

_translate_apostrophe_table = str.maketrans(
    APOSTROPHE_EQUIVALENTS
)


def normalize_apostrophes(s: str) -> str:
    """Normalize apostrophe-like characters to ASCII apostrophe."""

    if not isinstance(s, str):
        return s

    return s.translate(_translate_apostrophe_table)


# ============================================================
# PUNCTUATION PROTECTION
# ============================================================

COMMA_BEFORE_BREAK_RE = re.compile(
    r",(?=\s|$|[.,;:!?\'\"()])"
)

DOT_BEFORE_BREAK_RE = re.compile(
    r"\.(?=\s|$|\d|[\u0915])"
)

COLON_BEFORE_BREAK_RE = re.compile(
    r":(?=\s|$|\d)"
)

SLASH_BEFORE_BREAK_RE = re.compile(
    r"(?<![a-zA-Z;])\/(?![a-zA-Z;])"
)

OPEN_BRACKET_RE = re.compile(
    r"(?<=\s)\((?=\S)"
)

CLOSE_BRACKET_RE = re.compile(
    r"(?=\S)\((?<=\s)"
)


COMMA_MARKER = "ऀ"
DOT_MARKER = "ऎ"
COLON_MARKER = "ऄ"
SLASH_MARKER = "ऒ"
OPEN_MARKER = "ॵ"
CLOSE_MARKER = "ॶ"


def protect_punct(text: str) -> str:

    text = COMMA_BEFORE_BREAK_RE.sub(
        COMMA_MARKER,
        text
    )

    text = DOT_BEFORE_BREAK_RE.sub(
        DOT_MARKER,
        text
    )

    text = COLON_BEFORE_BREAK_RE.sub(
        COLON_MARKER,
        text
    )

    text = SLASH_BEFORE_BREAK_RE.sub(
        SLASH_MARKER,
        text
    )

    text = OPEN_BRACKET_RE.sub(
        OPEN_MARKER,
        text
    )

    text = CLOSE_BRACKET_RE.sub(
        CLOSE_MARKER,
        text
    )

    return text


def restore_punct(text: str) -> str:

    text = text.replace(
        COMMA_MARKER,
        ","
    )

    text = text.replace(
        DOT_MARKER,
        "."
    )

    text = text.replace(
        COLON_MARKER,
        ":"
    )

    text = text.replace(
        SLASH_MARKER,
        "/"
    )

    text = text.replace(
        OPEN_MARKER,
        "("
    )

    text = text.replace(
        CLOSE_MARKER,
        ")"
    )

    return text


# ============================================================
# TEXT PROCESSING
# ============================================================

def process_node(
    node,
    replacements,
    pattern
):

    def apply(s: str) -> str:

        if not s:
            return s

        # Normalize apostrophes
        s = normalize_apostrophes(s)

        # Protect punctuation
        s = protect_punct(s)

        # Apply replacements
        s = pattern.sub(
            lambda m: replacements.get(
                m.group(0),
                m.group(0)
            ),
            s
        )

        # Restore punctuation
        s = restore_punct(s)

        return s


    if node.text:
        node.text = apply(node.text)

    if node.tail:
        node.tail = apply(node.tail)

    for child in node:

        process_node(
            child,
            replacements,
            pattern
        )


# ============================================================
# COMPILE REPLACEMENT REGEX
# ============================================================

def compile_replacement_regex(
    replacements
):

    normalized = {}

    for key, value in replacements.items():

        normalized_key = normalize_apostrophes(
            key
        )

        normalized[normalized_key] = value


    # Longest keys first.
    #
    # This is important because, for example:
    #
    #     f[kz
    #
    # must be considered before:
    #
    #     f[k
    #
    # to prevent partial matching.

    sorted_keys = sorted(
        normalized.keys(),
        key=len,
        reverse=True
    )


    if not sorted_keys:

        # Prevent re.compile("") from matching
        # every position in the document.

        pattern = re.compile(
            r"(?!x)x"
        )

    else:

        pattern = re.compile(
            "|".join(
                re.escape(key)
                for key in sorted_keys
            )
        )


    return pattern, normalized


# ---------- Replacement logic ----------

myos = ["d%", "[k%", "x%", "?k%", "p%", "N%", "t%", ">%", "¥%", "V%", "B%", "M%", "<%", ".k%", "r%", "Fk%", "n%", "/k%", "u%", "i%",
"Q%", "c%", "Hk%", "e%", ";%", "j%", "y%", "o%", "‘k%", "l%", "g%", "G%", "{k%", "K%",
"'k", "'kk", "'kh", "f'k", "'kq", "'kw", "'ks", "'kS", "'ka", "'",
"“k", "“kk", "“kh", "f”k", "“kq", "“kw", "“ks", "“kS", "“ka", "“",
"Jk", " =kk", "fX", "f?", "f>", "f{", "fD", "fF", "fH", "fL", "fR", "/;k", "f'", "f\CHR$(34)+", "f[", "f.", "f/", "f=", "f}",
"fE", "fT", "fY", "fU", "fI", "fO", "fP", "fC", "UlZ", "Ul", "ElZ", "El", "OgZ", "Og", "OgsZ", "?;Z", "?;", "?;kZ", "?;k", "P;Z",
"P;", "P;kZ", "P;k", "D;Z", "D;", "D;kZ", "D;k", "E;Z", "E;", "E;kZ", "E;k", "YlZ", "Yl", "/;Z", "/;", "/;kZ", "/;k", "R;Z", "R;",
"R;kZ", "R;k", "Q~;Z", "Q~;", "Q~", "Q~;kZ", "Q~;k", "F;kZ", "F;Z", "F;", "F;k", "OghZ", "Ogh", "T;Z", "T;kZ", "T;", "T;k", "Y;Z", "Y;kZ", "Y;",
"Y;k", "U;Z", "U;kZ", "U;", "U;k", "I;Z", "I;kZ", "I;", "I;k", "O;Z", "O;kZ", "O;", "O;k", "\CHR$(34)+;Z", "\CHR$(34)+;kZ", "\CHR$(34)+;", "\CHR$(34)+;k", "L;Z", "L;kZ", "L;",
"L;k", "H;Z", "H;kZ", "H;", "H;k", "X;Z", "X;kZ", "X;", "X;k", "C;Z", "C;kZ", "C;", "C;k", "[;Z", "[;kZ", "[;", "[;k", "jkZ", "Dr", "Drh",
"Drha", ">ks", "vW", "fLo", "LF", "LFk", "LFkk", "LFkkZ",
"ç", "ê", "ë", "ì", "í", "ï", "ð", "ô", "ù", "Ÿ", "˜", "–", "—", "„", "‡", "‰", "™",
"Á", "Å", "Ì", "Í", "Î", "Ï", "Ñ", "Ô", "Ø", "Ù", "Ú", "Ý", "á", "â", "ã", "ä", "é", "æ", "ô", "ù",
"fDr", "f[kz", "fxz", "f?k", "f?kz", "ftz", ">kks", ">kkS", "f>k", ">kh", "fVz", "fMz",
"fR;", "fFkz", "FksZ", "fnz", "/kkh", "f/kz", "fuz", "fiz", "fQz", "D;Z", "D;kZ",
"[kZ", "[kkZ", "f[kZ", "[khZ", "[ksZ", "[kSZ", "[kksZ", "[kkSZ", "fxZ", "X;Z", "X;kZ", "?kZ", "?kkZ", "f?kZ", "?khZ", "?ksZ", "?kSZ", "?kksZ", "?kkSZ", "?;Z", 
"?;kZ", "fpZ", "P;Z", "P;kZ", "fNZ", "ftZ", "T;Z", "T;kZ", ">kZ", ">kkZ", ">kksZ", ">kkSZ", "f>kZ", ">khZ", ">ksZ", ">kSZ", "fVZ", "fMZ", ".kZ", ".kkZ",
".khZ", ".ksZ", ".kSZ", ".kksZ", ".kkSZ", "frZ", "FkkZ", "fFkZ", "FkSZ", "FkksZ", "FkkSZ", "F;Z", "fnZ", "/kZ", "/kkZ", "/kksZ", "f/kZ", "/khZ", "/ksZ", "/kSZ",
"/kkSZ", "fuZ", "U;Z", "U;kZ", "UlZ", "fiZ", "I;Z", "I;kZ", "fQZ", "Q~;Z", "Q~;kZ", "C;Z", "C;kZ", "HkZ", "HkkZ", "HksZ", "HkSZ", "HkksZ", "HkkSZ", "H;Z",
"H;kZ", "E;Z", "E;kZ", "ElZ", "fyZ", "Y;Z", "Y;kZ", "YlZ", "foZ", "O;Z", "O;kZ", "OgZ", "OghZ", "OgsZ", "'kZ", "'kkZ", "f'kZ", "'khZ", "'ksZ", "'kSZ",
"'kksZ", "'kkSZ", "”kZ", "”kkZ", "f”kZ", "”khZ", "flZ", "fgZ", "fY", "fO", "foz", "f'", "fL", "fLr", "fLFk",
"yka", "”k", "”ka", "”kk", "”kkW", "”kkS", "”kks", "”kh", "”kq", "”kw", "”kW", "”ks", "”kS", "”kkZ", "”kZ", "f”kZ", "”khZ", "”k", "”", "FkhZ", 
    "f.kZ", "F;kZ", "FkZ", "\CHR$(34)+kkZ", "?k", "?", "\CHR$(34)+khZ", "\CHR$(34)+k", "\CHR$(34)", "f.k", ".k", ".", "f?k", "f>", "fFk", "f/k", "fHk", "f'k", "f{k", "f[k", 
    "?k", "?ka", "?k%", "?kq", "?kw", "?kW", "'k", "'ka", "'k%", "'kq", "'kw", "'kW", "[k", "[ka", "[kkW", "[kW", "[k%", "[kq", "[kw", "{k", 
    "{ka", "{k%", "{kh", "{kq", "{kw", "{kW", "{ks", "{kS", "/k", "/ka", "/k%", "/kq", "/kw", "/kW", "Fk", "Fka", "FkkW", "Fk%", "Fkq", "Fkw", 
    "FkW", "Hk", "HkW", "Hka", "Hk%", "Hkq", "Hkw", ">", "X", "U", "T", "R", "P", "O", "L", "I", "H", "F", "E", "D", 
    "C", "Y", "yZ", "ysZ", "ySZ", "ys", "yS", "YlZ", "Yl", "ykZ", "ykW", "yksZ", "ykSZ", "ykS", "yks", "yk", "yhZ", "yh", "Y;Z", "Y;kZ", 
    "Y;k", "Y;", "xzks", "xzkS", "xzk", "xZ", "xz", "xsZ", "xSZ", "xs", "xS", "xs", "xkZ", "xkW", "xkSZ", "xksZ", "xks", "xkS", "xk", "xhZ", 
    "xh", "X;Z", "X;kZ", "X;k", "X;", "Vzks", "VzkS", "Vzk", "VZ", "Vz", "VsZ", "VSZ", "Vs", "VS", "VkZ", "vkW", "VkW", "VksZ", "VkSZ", "vks", 
    "vkS", "Vks", "VkS", "vk", "Vk", "VhZ", "Vh", "uzks", "uzkS", "uZ", "uz", "usZ", "uSZ", "us", "uS", "UlZ", "Ul", "ukZ", "ukW", "uksZ", 
    "ukSZ", "ukS", "uks", "uk", "uhZ", "uh", "U;Z", "U;kZ", "U;k", "U;", "tzks", "tzkS", "tZ", "tz", "tsZ", "tSZ", "ts", "tS", "tkZ", "tkW", 
    "tksZ", "tkSZ", "tkS", "tks", "tk", "thZ", "th", "T;Z", "T;kZ", "T;k", "T;", "rZ", "rsZ", "rSZ", "rs", "rS", "rkZ", "rkW", "rksZ", "rkSZ", 
    "rkS", "rks", "rk", "rhZ", "rh", "R;Z", "R;w", "R;s", "R;S", "R;q", "R;kZ", "R;ks", "R;kS", "R;k", "R;k", "R;h", "R;a", "R;%", "R;", "R;", 
    "Qzks", "QzkS", "Qzk", "QZ", "Qz", "QsZ", "QSZ", "Qs", "QS", "QkZ", "QksZ", "QkSZ", "QkS", "Qks", "Qk", "QhZ", "Qh", "Q~", "Q~;Z", "Q~;kZ", 
    "Q~;k", "Q~;", "pzks", "pzkS", "pZ", "pZ", "pZ", "psZ", "pSZ", "ps", "pS", "pkZ", "pkW", "pksZ", "pkSZ", "pks", "pkS", "pk", "phZ", "ph", 
    "P;Z", "P;kZ", "P;k", "P;", "ozw", "ozq", "ozks", "ozkS", "ozk", "oZ", "oz", "osZ", "oSZ", "os", "oS", "okZ", "okW", "oksZ", "okSZ", "okS", 
    "oks", "ok", "ohZ", "oh", "OgZ", "OgsZ", "OghZ", "Ogh", "Og", "O;Z", "O;kZ", "O;k", "O;", "nzks", "nzkS", "Nzks", "Nzks", "NzkS", "nzk", "nZ", 
    "NZ", "nz", "NSZ", "NsZ", "nsZ", "nSZ", "Ns", "NS", "ns", "nS", "NkZ", "nkZ", "nkW", "NksZ", "NkSZ", "NksZ", "nksZ", "nkSZ", "Nks", "NkS", 
    "nks", "nkS", "Nk", "nk", "NhZ", "nhZ", "Nh", "nh", "Mzks", "MzkS", "Mzk", "MZ", "Mz", "MsZ", "MSZ", "Ms", "MS", "mq", "MkZ", "MkW", 
    "MksZ", "MkSZ", "Mks", "MkS", "Mk", "MhZ", "Mh", "lzks", "lzkS", "lZ", "lsZ", "lSZ", "ls", "lS", "lkZ", "lkW", "lksZ", "lkSZ", "lks", "lkS", 
    "lk", "lhZ", "lh", "L;Z", "L;kZ", "L;k", "L;", "KZ", "Kks", "KkS", "Kk", "jkZ", "jkW", "jks", "jkS", "Jks", "JkS", "jk", "Jk", "izks", 
    "izkS", "izk", "iZ", "iz", "isZ", "iSZ", "is", "iS", "ikZ", "ikW", "iksZ", "ikSZ", "ikS", "iks", "ik", "ihZ", "ih", "I;Z", "I;kZ", "I;k", 
    "I;", "Hkzks", "HkzkS", "Hkzk", "HkZ", "Hkz", "HkW", "HksZ", "HkSZ", "Hks", "HkS", "HkkZ", "HkksZ", "HkkSZ", "Hkks", "HkkS", "Hkk", "HkhZ", "Hkh", "H;Z", 
    "H;kZ", "H;k", "H;", "gZ", "gsZ", "gSZ", "gs", "gS", "gkZ", "gkW", "gkW", "gksZ", "gkSZ", "gkS", "gks", "Gks", "GkS", "gk", "Gk", "ghZ", 
    "gh", "fyZ", "fy", "fY", "fxz", "fxZ", "fx", "fX", "fVz", "fVZ", "fV", "fuZ", "fuz", "fu", "fU", "ftz", "ftZ", "ft", "fT", "frZ", 
    "fr", "fR", "fR;", "fQZ", "fQz", "fQ", "fpZ", "fpz", "fp", "fP", "foZ", "foz", "fo", "fO", "fNZ", "fnZ", "fnz", "fN", "fn", "fMz", 
    "fMZ", "fM", "flZ", "flz", "fLr", "fLFk", "fl", "fL", "Fkzks", "FkzkS", "Fkzk", "FkZ", "Fkz", "FksZ", "FkSZ", "Fks", "FkS", "FkkZ", "FkkW", "FkksZ", 
    "FkkSZ", "Fkks", "FkkS", "Fkk", "FkhZ", "Fkh", "fK", "fj", "fJ", "fiZ", "fiz", "fi", "fI", "fHkZ", "fHkz", "fHk", "fH", "fgZ", "fGk", "fg", 
    "fG", "fFkz", "fFkZ", "fFk", "fF", "feZ", "fez", "fe", "fE", "fdz", "fdZ", "fDr", "fd", "fD", "fcZ", "fcz", "fc", "fC", "fBz", "fBZ", 
    "fB", "f>kZ", "f>k", "f>", "f=k", "f=", "f<z", "f<Z", "f<", "f/kZ", "f/kz", "f/k", "f/", "f}", "f{k", "f{", "f[kz", "f[kZ", "f[k", "f[", 
    "f'p", "f'kZ", "f'k", "f'", "f.kZ", "f.kz", "f.k", "f?kz", "f?kZ", "f?k", "f?", "f;Z", "f;z", "F;Z", "F;kZ", "F;k", "f;", "F;", "ezw", 
    "ezs", "ezS", "ezq", "ezks", "ezkS", "ezk", "ezh", "eza", "ez%", "eZ", "ez", "esZ", "eSZ", "es", "eS", "ElZ", "El", "ekZ", "ekW", "eksZ", 
    "ekSZ", "ekS", "eks", "ek", "ehZ", "eh", "E;Z", "E;kZ", "E;k", "E;", "dzks", "dzkS", "dzk", "dZ", "dz", "dsZ", "dSZ", "ds", "dS", "dkZ", 
    "dkW", "dksZ", "dkSZ", "dkS", "dks", "dk", "dk", "dhZ", "dh", "D;Z", "D;kZ", "D;k", "D;", "czks", "czkS", "czk", "cZ", "cz", "csZ", "cSZ", 
    "cs", "cS", "ckZ", "ckW", "cksZ", "ckSZ", "cks", "ckS", "ck", "chZ", "ch", "C;Z", "C;kZ", "C;k", "C;", "Bzks", "BzkS", "BZ", "bZ", "Bz", 
    "BsZ", "BSZ", "Bs", "Bs", "BS", "BkZ", "BksZ", "BkSZ", "Bks", "BkS", "Bk", "BhZ", "Bh", "|k", ">kZ", ">ksZ", ">kSZ", ">ks", ">kS", ">kkZ", 
    ">kksZ", ">kkSZ", ">kks", ">kkS", ">khZ", ">kh", ">k", "=ks", "=kks", "=kkS", "=kk", "=k", "<zks", "<zkS", "<Z", "<z", "<sZ", "<SZ", "<s", "<S", 
    "<s", "<S", "<kZ", "<ksZ", "<kSZ", "<ks", "<kS", "<k", "<hZ", "<h", "<h", "/kzks", "/kzkS", "/kzk", "/kZ", "/kz", "/ksZ", "/kSZ", "/ks", "/kS", 
    "/kkZ", "/kksZ", "/kkSZ", "/kks", "/kkS", "/kkh", "/kk", "/khZ", "/khZ", "/kh", "/;Z", "/;kZ", "/;k", "/;k", "/;", "{kks", "{kkS", "{kk", "[kzs", "[kzs", 
    "[kzks", "[kzkS", "[kzk", "[kZ", "[kz", "[kW", "[ksZ", "[kSZ", "[ks", "[kS", "[kkZ", "[kksZ", "[kkSZ", "[kkS", "[kks", "[kk", "[khZ", "[kh", "[;Z", "[;kZ", 
    "[;k", "[;", "'kZ", "'ksZ", "'kSZ", "'ks", "'kS", "'kkZ", "'kksZ", "'kkSZ", "'kks", "'kkS", "'kk", "'khZ", "'kh", ".kzks", ".kzkS", ".kZ", ".ksZ", ".ksZ", 
    ".kSZ", ".ks", ".kS", ".kkZ", ".kksZ", ".kkSZ", ".kks", ".kkS", ".kk", ".khZ", ".khZ", ".kh", "?kzks", "?kzkS", "?kzk", "?kZ", "?kz", "?ksZ", "?kSZ", "?ks", 
    "?kS", "?kkZ", "?kksZ", "?kkSZ", "?kks", "?kkS", "?kk", "?khZ", "?kh", "?;Z", "?;kZ", "?;k", "?;", ";zks", ";zkS", ";Z", ";sZ", ";SZ", ";s", ";S", 
    ";kZ", ";ksZ", ";kSZ", ";ks", ";kS", ";k", ";hZ", ";h", ",s", "Z", "z", "y", "x", "W", "w", "V", "v", "u", "t", "S", 
    "s", "r", "Q", "q", "p", "o", "N", "n", "M", "m", "l", "K", "k", "J", "j", "i", "Hk", "h", "G", "g", 
    "Fk", "f", "e", "d", "c", "B", "b", "A", "a", "$", "~", ">k", "^", "`", "&", "\\", "/k", "*", "{k", ",", 
    "[k", "", "'k", ".k", "?k", "!", "9", "8", "7", "6", "5", "4", "3", "2", "1", "0", "|", "=", "<", "+", 
    "}", "-", "%", ";", "]", "(", ")", "#", "_", "½", "¼", "/", "@", ":", ", ", ". ", ": ", " (", ") "]

myts = ["कः", "खः", "गः", "घः", "चः", "छः", "जः", "झः", "ञः", "टः", "ठः", "डः", "ढः", "णः", "तः", "थः", "दः", "धः", "नः", "पः",
"फः", "बः", "भः", "मः", "यः", "रः", "लः", "वः", "शः", "सः", "हः", "ळः", "क्षः", "ज्ञः",
"श", "शा", "शी", "शि", "शु", "शू", "शे ", "शै", "शं", "श्",
"ष", "षा", "षी", "षि", "षु", "षू", "षे ", "षै", "षं", "ष्", 
"श्रा", "त्रा", "ग्‍ि", "घ्‍ि", "झि", "क्ष्‍ि", "क्‍ि", "थ्‍ि", "भ्‍ि", "स्‍ि", "त्‍ि", "ध्या", "श्‍ि", "ष्‍ि", "ख्‍ि", "ण्‍ि", "ध्‍ि", "त्रि", "द्वि", "म्‍ि",
"ज्‍ि", "ल्‍ि", "न्‍ि", "प्‍ि", "व्‍ि", "च्‍ि", "ब्‍ि", "र्न्स", "न्स", "र्म्स", "म्स", "र्व्ह", "व्ह", "र्व्हे", "र्घ्य", "घ्य", "र्घ्या", "घ्या", "र्च्य", "च्य",
"र्च्या", "च्या", "र्क्य", "क्य", "र्क्या", "क्या", "र्म्य", "म्य", "र्म्या", "म्या", "र्ल्स", "ल्स", "र्ध्य", "ध्य", "र्ध्या", "ध्या", "र्त्य", "त्य", "र्त्या", "त्या",
"र्फ्य", "फ्य", "फ्", "र्फ्या", "फ्या", "र्थ्या", "र्थ्य", "थ्य", "थ्या", "र्व्ही", "व्ही", "र्ज्य", "र्ज्या", "ज्य", "ज्या", "र्ल्य", "र्ल्या", "ल्य", "ल्या", "र्न्य",
"र्न्या", "न्य", "न्या", "र्प्य", "र्प्या", "प्य", "प्या", "र्व्य", "र्व्या", "व्य", "व्या", "र्ष्य", "र्ष्या", "ष्य", "ष्या", "र्स्य", "र्स्या", "स्य", "स्या", "र्भ्य",
"र्भ्या", "भ्य", "भ्या", "र्ग्य", "र्ग्या", "ग्य", "ग्या", "र्ब्य", "र्ब्या", "ब्य", "ब्या", "र्ख्य", "र्ख्या", "ख्य", "ख्या", "र्रा", "क्‍त", "क्‍ती", "क्‍तीं", "झाे",
"ॲ", "स्वि", "स्‍थ्‍", "स्‍थ", "स्‍था", "र्स्था",
"प्र", "ट्ट", "ट्ठ", "ड्ड", "द्द", "ड्ढ", "ठ्ठ", "क्क", "द्म", "त्त्", "द्भ", "दृ", "कृ", "ह्म", "ह्व", "क्त", "न्न",
"प्र", "ऊ", "द्द", "ट्ट", "ट्ठ", "ड्ड", "कृ", "ड्ढ", "क्र", "त्त", "ऱ्", "फ्र", "ह्य", "हृ", "ह्म", "क्त", "न्न", "द्र", "क्क", "द्म",
"क्ति", "ख्रि", "ग्रि", "घि", "घ्रि", "ज्रि", "झाे", "झाै", "झि", "झी", "ट्रि", "ड्रि",
"त्यि", "थ्रि", "थ्रे", "द्रि", "धी", "ध्रि", "न्रि", "प्रि", "फ्रि", "र्क्य", "र्क्या",
"र्ख", "र्खा", "र्खि", "र्खी", "र्खे", "र्खै", "र्खो", "र्खो", "र्गि", "र्ग्य", "र्ग्या", "र्घ", "र्घा", "र्घि", "र्घी", "र्घे", "र्घै", "र्घो", "र्घौ", "र्घ्य",
"र्घ्या", "र्चि", "र्च्य", "र्च्या", "र्छि", "र्जि", "र्ज्य", "र्ज्या", "र्झ", "र्झा", "र्झाे", "र्झाै", "र्झि", "र्झी", "र्झे", "र्झै", "र्टि", "र्डि", "र्ण", "र्णा",
"र्णी", "र्णे", "र्णै", "र्णो", "र्णौ", "र्ति", "र्था", "र्थि", "र्थै", "र्थो", "र्थौ", "र्थ्य", "र्दि", "र्ध", "र्धा", "र्धाे", "र्धि", "र्धी", "र्धे", "र्धै",
"र्धो", "र्नि", "र्न्य", "र्न्या", "र्न्स", "र्पि", "र्प्य", "र्प्या", "र्फि", "र्फ्य", "र्फ्या", "र्ब्य", "र्ब्या", "र्भ", "र्भा", "र्भे", "र्भै", "र्भो", "र्भौ", "र्भ्य",
"र्भ्या", "र्म्य", "र्म्या", "र्म्स", "र्लि", "र्ल्य", "र्ल्या", "र्ल्स", "र्वि", "र्व्य", "र्व्या", "र्व्ह", "र्व्ही", "र्व्हे", "र्श", "र्शा", "र्शि", "र्शी", "र्शे", "र्शै",
"र्शो", "र्शौ", "र्ष", "र्षा", "र्षि", "र्षी", "र्सि", "र्हि", "लि्", "वि्", "व्रि", "शि्", "सि्", "स्ति", "स्थि",
"लां", "ष", "षं", "षा", "षाॅ", "षौ", "षो", "षी", "षु", "षू", "षॅ", "षे", "षै", "र्षा", "र्ष", "र्षि", "र्षी", "ष", "ष्", "र्थी", 
    "र्णि", "र्थ्या", "र्थ", "र्षा", "घ", "घ्", "र्षी", "ष", "ष्", "णि", "ण", "ण्", "घि", "झि", "थि", "धि", "भि", "शि", "क्षि", "खि", 
    "घ", "घं", "घः ", "घु", "घू", "घॅ", "श", "शं", "श:", "शु", "शू", "शॅ", "ख", "खं", "खाॅ", "खॅ", "ख:", "खु", "खू", "क्ष", 
    "क्षं", "क्ष:", "क्षी", "क्षु", "क्षू", "क्षॅ", "क्षे", "क्षै", "ध", "धं", "ध:", "धु", "धू", "धॅ", "थ", "थं", "थॉ", "थ:", "थु", "थू", 
    "थॅ", "भ", "भॅ", "भं", "भ:", "भु", "भू", "झ", "ग्", "न्", "ज्", "त्", "च्", "व्", "स्", "प्", "भ्", "थ्", "म्", "क्", 
    "ब्", "ल्", "र्ल", "र्ले", "र्लै", "ले", "लै", "र्ल्स", "ल्स", "र्ला", "लॉ", "र्लो", "र्लौ", "लौ", "लो", "ला", "र्ली", "ली", "र्ल्य", "र्ल्या", 
    "ल्या", "ल्य", "ग्रो", "ग्रौ", "ग्रा", "र्ग", "ग्र", "र्गे", "र्गै", "गे", "गै", "गे", "र्गा", "गॉ", "र्गौ", "र्गो", "गो", "गौ", "गा", "र्गी", 
    "गी", "र्ग्य", "र्ग्या", "ग्या", "ग्य", "ट्रो", "ट्रौ", "ट्रा", "र्ट", "ट्र", "र्टे", "र्टै", "टे", "टै", "र्टा", "ऑ", "टॉ", "र्टो", "र्टौ", "ओ", 
    "औ", "टो", "टौ", "आ", "टा", "र्टी", "टी", "न्रो", "न्रौ", "र्न", "न्र", "र्ने", "र्नै", "ने", "नै", "र्न्स", "न्स", "र्ना", "नॉ", "र्नो", 
    "र्नौ", "नौ", "नो", "ना", "र्नी", "नी", "र्न्य", "र्न्या", "न्या", "न्य", "ज्रो", "ज्रौ", "र्ज", "ज्र", "र्जे", "र्जै", "जे", "जै", "र्जा", "जॉ", 
    "र्जो", "र्जौ", "जौ", "जो", "जा", "र्जी", "जी", "र्ज्य", "र्ज्या", "ज्या", "ज्य", "र्त", "र्ते", "र्तै", "ते", "तै", "र्ता", "तॉ", "र्तो", "र्तौ", 
    "तौ", "तो", "ता", "र्ती", "ती", "र्त्य", "त्यू", "त्ये", "त्यै", "त्यु", "र्त्या", "त्यो", "त्यौ", "त्या", "त्या", "त्यी", "त्यं", "त्यः", "त्य", "त्य", 
    "फ्रो", "फ्रौ", "फ्रा", "र्फ", "फ्र", "र्फे", "र्फै", "फे", "फै", "र्फा", "र्फो", "र्फौ", "फौ", "फो", "फा", "र्फी", "फी", "फ्", "र्फ्य", "र्फ्या", 
    "फ्या", "फ्य", "च्रो", "च्रौ", "र्च", "र्च", "र्च", "र्चे", "र्चै", "चे", "चै", "र्चा", "चॉ", "र्चो", "र्चौ", "चो", "चौ", "चा", "र्ची", "ची", 
    "र्च्य", "र्च्या", "च्या", "च्य", "व्रू", "व्रु", "व्रो", "व्रौ", "व्रा", "र्व", "व्र", "र्वे", "र्वै", "वे", "वै", "र्वा", "वॉ", "र्वो", "र्वौ", "वौ", 
    "वो", "वा", "र्वी", "वी", "र्व्ह", "र्व्हे", "र्व्ही", "व्ही", "व्ह", "र्व्य", "र्व्या", "व्या", "व्य", "द्रो", "द्रौ", "छ्रो", "छ्रो", "छ्रौ", "द्रा", "र्द", 
    "र्छ", "द्र", "र्छै", "र्छे", "र्दे", "र्दै", "छे", "छै", "दे", "दै", "र्छा", "र्दा", "दॉ", "र्छो", "र्छौ", "र्छो", "र्दो", "र्दौ", "छो", "छौ", 
    "दो", "दौ", "छा", "दा", "र्छी", "र्दी", "छी", "दी", "ड्रो", "ड्रौ", "ड्रा", "र्ड", "ड्र", "र्डे", "र्डै", "डे", "डै", "ऊ", "र्डा", "डॉ", 
    "र्डो", "र्डौ", "डो", "डौ", "डा", "र्डी", "डी", "स्रो", "स्रौ", "र्स", "र्से", "र्सै", "से", "सै", "र्सा", "सॉ", "र्सो", "र्सौ", "सो", "सौ", 
    "सा", "र्सी", "सी", "र्स्य", "र्स्या", "स्या", "स्य", "र्ज्ञ", "ज्ञो", "ज्ञौ", "ज्ञा", "र्रा", "रॉ", "रो", "रौ", "श्रो", "श्रौ", "रा", "श्रा", "प्रो", 
    "प्रौ", "प्रा", "र्प", "प्र", "र्पे", "र्पै", "पे", "पै", "र्पा", "पॉ", "र्पो", "र्पौ", "पौ", "पो", "पा", "र्पी", "पी", "र्प्य", "र्प्या", "प्या", 
    "प्य", "भ्रो", "भ्रौ", "भ्रा", "र्भ", "भ्र", "भॉ", "र्भे", "र्भै", "भे", "भै", "र्भा", "र्भो", "र्भौ", "भो", "भौ", "भा", "र्भी", "भी", "र्भ्य", 
    "र्भ्या", "भ्या", "भ्य", "र्ह", "र्हे", "र्है", "हे", "है", "र्हा", "हॉ", "हॉ", "र्हो", "र्हौ", "हौ", "हो", "ळो", "ळौ", "हा", "ळा", "र्ही", 
    "ही", "र्लि", "लि", "ल्‍ि", "ग्रि", "र्गि", "गि", "ग्‍ि", "ट्रि", "र्टि", "टि", "र्नि", "न्रि", "नि", "न्‍ि", "ज्रि", "र्जि", "जि", "ज्‍ि", "र्ति", 
    "ति", "त्‍ि", "त्यि", "र्फि", "फ्रि", "फि", "र्चि", "च्रि", "चि", "च्‍ि", "र्वि", "व्रि", "वि", "व्‍ि", "र्छि", "र्दि", "द्रि", "छि", "दि", "ड्रि", 
    "र्डि", "डि", "र्सि", "स्रि", "स्ति", "स्थि", "सि", "स्‍ि", "थ्रो", "थ्रौ", "थ्रा", "र्थ", "थ्र", "र्थे", "र्थै", "थे", "थै", "र्था", "थॉ", "र्थो", 
    "र्थौ", "थो", "थौ", "था", "र्थी", "थी", "ज्ञि", "रि", "श्रि", "र्पि", "प्रि", "पि", "प्‍ि", "र्भि", "भ्रि", "भि", "भ्‍ि", "र्हि", "भि", "हि", 
    "ळि", "थ्रि", "र्थि", "थि", "थ्‍ि", "र्मि", "म्रि", "मि", "म्‍ि", "क्रि", "र्कि", "क्ति", "कि", "क्‍ि", "र्बि", "ब्रि", "बि", "ब्‍ि", "ठ्रि", "र्ठि", 
    "ठि", "र्झि", "झि", "झि", "त्रि", "त्रि", "ढ्रि", "र्ढि", "ढि", "र्धि", "ध्रि", "धि", "ध्‍ि", "द्वि", "क्षि", "क्ष्‍ि", "ख्रि", "र्खि", "खि", "ख्‍ि", 
    "श्चि", "र्शि", "शि", "श्‍ि", "र्णि", "ण्रि", "णि", "घ्रि", "र्घि", "घि", "घ्‍ि", "र्यि", "य्रि", "र्थ्य", "र्थ्या", "थ्या", "यि", "थ्य", "म्रू", 
    "म्रे", "म्रै", "म्रु", "म्रो", "म्रौ", "म्रा", "म्री", "म्रं", "म्रः", "र्म", "म्र", "र्मे", "र्मै", "मे", "मै", "र्म्स", "म्स", "र्मा", "मॉ", "र्मो", 
    "र्मौ", "मौ", "मो", "मा", "र्मी", "मी", "र्म्य", "र्म्या", "म्या", "म्य", "क्रो", "क्रौ", "क्रा", "र्क", "क्र", "र्के", "र्कै", "के", "कै", "र्का", 
    "कॉ", "र्को", "र्कौ", "कौ", "को", "का", "का", "र्की", "की", "र्क्य", "र्क्या", "क्या", "क्य", "ब्रो", "ब्रौ", "ब्रा", "र्ब", "ब्र", "र्बे", "र्बै", 
    "बे", "बै", "र्बा", "बॉ", "र्बो", "र्बौ", "बो", "बौ", "बा", "र्बी", "बी", "र्ब्य", "र्ब्या", "ब्या", "ब्य", "ठ्रो", "ठ्रौ", "र्ठ", "ई", "ठ्र", 
    "र्ठे", "र्ठै", "ठे", "ठे", "ठै", "र्ठा", "र्ठो", "र्ठौ", "ठो", "ठौ", "ठा", "र्ठी", "ठी", "द्या", "र्झ", "र्झे", "र्झै", "झे", "झै", "र्झा", 
    "र्झो", "र्झौ", "झो", "झौ", "र्झी", "झी", "झा", "त्रे", "त्रो", "त्रौ", "त्रा", "त्रा", "ढ्रो", "ढ्रौ", "र्ढ", "ढ्र", "र्ढे", "र्ढै", "ढे", "ढै", 
    "ढे", "ढै", "र्ढा", "र्ढो", "र्ढौ", "ढो", "ढौ", "ढा", "र्ढी", "ढी", "ढी", "ध्रो", "ध्रौ", "ध्रा", "र्ध", "ध्र", "र्धे", "र्धै", "धे", "धै", 
    "र्धा", "र्धो", "र्धो", "धो", "धौ", "धी", "धा", "र्धी", "र्धी", "धी", "र्ध्य", "र्ध्या", "ध्या", "ध्या", "ध्य", "क्षो", "क्षौ", "क्षा", "ख्रे", "ख्रे", 
    "ख्रो", "ख्रौ", "ख्रा", "र्ख", "ख्र", "खॉ", "र्खे", "र्खै", "खे", "खै", "र्खा", "र्खो", "र्खौ", "खौ", "खो", "खा", "र्खी", "खी", "र्ख्य", "र्ख्या", 
    "ख्या", "ख्य", "र्श", "र्शे", "र्शै", "शे", "शै", "र्शा", "र्शो", "र्शौ", "शो", "शौ", "शा", "र्शी", "शी", "ण्रो", "ण्रौ", "र्ण", "र्णे", "र्णे", 
    "र्णै", "णे", "णै", "र्णा", "र्णो", "र्णौ", "णो", "णौ", "णा", "र्णी", "र्णी", "णी", "घ्रो", "घ्रौ", "घ्रा", "र्घ", "घ्र", "र्घे", "र्घै", "घे", 
    "घै", "र्घा", "र्घो", "र्घौ", "घो", "घौ", "घा", "र्घी", "घी", "र्घ्य", "र्घ्या", "घ्या", "घ्य", "य्रो", "य्रौ", "र्य", "र्ये", "र्यै", "ये", "यै", 
    "र्या", "र्यो", "र्यौ", "यो", "यौ", "या", "र्यी", "यी", "ऐ", "र्‍", "्र", "ल", "ग", "ॅ", "ू", "ट", "अ", "न", "ज", "ै", 
    "े", "त", "फ", "ु", "च", "व", "छ", "द", "ड", "उ", "स", "ज्ञ", "ा", "श्र", "र", "प", "भ", "ी", "ळ", "ह", 
    "थ", "ि", "म", "क", "ब", "ठ", "इ", "।", "ं", "ऱ्", "्", "झा", "'", "ृ", "-", "?", "ध", "×", "क्ष", "ए", 
    "ख", "", "श", "ण", "घ", "!", "९", "८", "७", "६", "५", "४", "३", "२", "१", "०", "द्य", "त्र", "ढ", "़", 
    "द्व", ".", "ः", "य", ",", ";", "द्ध", "रु", "ऋ", ")", "(", "ध्", "/", "रू", ", ", ". ", ": ", " (", ") "]


replacements = dict(zip(myos, myts))

#exclude_list = ["No", "ADMN", "Dtd", "Outward", "Dt"]

exclude_list_all = ["Abdul", "able",  "about", "above",  "abused",  "accepted",  "account",  "accused",  "acquisition",  "Act",  "Adult",  "aforesaid",  "Age",  "Aged",  "agreement",  "Agriculturist",  "Ahmed",  "alias",  "All",  "along",  "also",  "alter",  "Amendment",  "amount",  "an",  "and",  "animal",  "animals",  "Ans",  "any",  "anything",  "April",  "are",  "Arms",  "as",  "assault",  "assaulted",  "assembly",  "assure",  "at",  "attempted",  "August",  "bag",  "Bank",  "bar",  "be",  "bearing",  "before",  "being",  "believe",  "belonging",  "between",  "black",  "blows",  "board",  "Bombay",  "Both",  "bound",  "Branch",  "breach",  "breadth",  "break",  "breakfast",  "brick",  "buds",  "bullocks",  "Businessman",  "but",  "by",  "bye",  "cage",  "can",  "capable",  "care",  "carried",  "carries",  "carrying",  "cart",  "Castes",  "cause",  "caused",  "causing",  "certain",  "certificate",  "Certified",  "chain",  "chained",  "Chapter",  "charge",  "Chassis",  "cheated",  "cheating",  "city",  "CLASS",  "Code",  "cognizance",  "Collector",  "Com",  "committed",  "committing",  "common",  "complainant",  "complained",  "complying",  "compound",  "computer",  "condition",  "confined",  "confines",  "consent",  "consequence",  "Contents",  "contract",  "Contractor",  "converted",  "conveys",  "copies",  "cord",  "Corporation",  "councilor",  "counterfeit",  "counterfeited",  "country",  "COURT",  "created",  "criminal",  "Cruelty",  "currency",  "damage",  "date",  "Dated",  "day",  "dead",  "deadly",  "death",  "December",  "deliver",  "demand",  "demanding",  "denomination",  "destroy",  "details",  "deter",  "did",  "direct",  "discharge",  "discharging",  "dishonestly",  "Dist",  "District",  "do",  "document",  "does",  "done",  "dose",  "Dot",  "driver",  "driving",  "duplex",  "duty",  "dwelling",  "dyes",  "either",  "entering",  "entrusted",  "etc",  "execution",  "explained",  "extracts",  "failed",  "fear",  "Fifthly",  "File",  "filthy",  "FIRST",  "fist",  "fists",  "fly",  "follows",  "for",  "force",  "forged",  "fort",  "found",  "four",  "Fourthly",  "from",  "front",  "funds",  "further",  "furtherance",  "Gala",  "gate",  "gave",  "Given",  "Government",  "Govt",  "Gram",  "Green",  "grievous",  "guilty",  "hand",  "have",  "having",  "he",  "heavy",  "height",  "her",  "hereby",  "Hero",  "him",  "his",  "Honda",  "Hotel",  "hours",  "house",  "hrs",  "human",  "hurt",  "IN",  "incident",  "Indian",  "inducing",  "infliction",  "informant",  "injury",  "Inspector",  "instrument",  "Instruments",  "insufficient",  "insulted",  "insurance",  "intending",  "intent",  "intention",  "intentionally",  "interest",  "interested",  "intimidation",  "into",  "iron",  "is",  "issued",  "it",  "its",  "JUDICIAL",  "June",  "keeps",  "kept",  "key",  "Khan",  "kick",  "kill",  "knife",  "knowing",  "knowledge",  "language",  "lat",  "Law",  "lawful",  "laxer",  "length",  "license",  "likely",  "liquor",  "loss",  "Ltd",  "made",  "MAGISTRATE",  "Maharashtra",  "make",  "Manager",  "manner",  "me",  "means",  "measure",  "measures",  "member",  "Mobile",  "more",  "mortgaged",  "Motor",  "movement",  "moving",  "Municipal",  "my",  "Nagpur",  "Name",  "namely",  "near",  "Negotiable",  "No",  "Nos",  "not",  "note",  "notes",  "notice",  "number",  "object",  "obstructed",  "occurrence",  "October",  "OF",  "off",  "office",  "official",  "ok#Gdj]4-euksgj",  "old",  "on",  "one",  "open",  "Opp",  "opportunity",  "or",  "other",  "over",  "owner",  "pain",  "papers",  "part",  "PARTICULAR",  "PARTICULARS",  "party",  "pass",  "passenger",  "Pat",  "Path",  "pay",  "peace",  "Penal",  "permit",  "person",  "persons",  "pipe",  "pipes",  "pk",  "place",  "plead",  "plot",  "Police",  "policy",  "position",  "possessing",  "possession",  "preparations",  "presence",  "prevent",  "Prevention",  "prior",  "produce",  "Prohibition",  "property",  "prosecution",  "protect",  "provocation",  "public",  "punishable",  "purpose",  "purposed",  "put",  "quarter",  "quarters",  "read",  "reason",  "reasonable",  "reasons",  "received",  "receptacle",  "registration",  "removed",  "report",  "reported",  "reputation",  "requirement",  "respect",  "restaurant",  "restraint",  "rioting",  "road",  "robbed",  "robbery",  "room",  "rs",  "running",  "rupees",  "said",  "sale",  "same",  "satisfactorily",  "school",  "seal",  "sealed",  "Sec",  "section",  "security",  "sent",  "September",  "servant",  "Service",  "set",  "shall",  "shop",  "short",  "shown",  "signed",  "situated",  "Slaughter",  "slaughtering",  "some",  "sons",  "space",  "specify",  "square",  "star",  "State",  "Station",  "sticks",  "stipulated",  "subject",  "such",  "suffering",  "sufficiently",  "sun",  "sunrise",  "sword",  "tailoring",  "take",  "taking",  "tethered",  "than",  "That",  "THE",  "theft",  "their",  "them",  "themselves",  "thereby",  "third",  "Thirdly",  "this",  "thou",  "though",  "threat",  "threatened",  "threatening",  "threats",  "threw",  "through",  "thus",  "time",  "to",  "total",  "town",  "trespass",  "tried",  "trust",  "ts",  "unauthorized",  "under",  "uniform",  "unknown",  "unlawful",  "unnecessary",  "unreasonable",  "unreasonably",  "upon",  "us",  "use",  "used",  "using",  "valid",  "valuable",  "vehicle",  "Vehicles",  "vernacular",  "village",  "violence",  "voluntarily",  "was",  "weapon",  "weapons",  "well",  "were",  "wheeler",  "whereupon",  "whether",  "which",  "whole",  "whom",  "whose",  "will",  "wine",  "wit",  "with",  "within",  "without",  "wooden",  "work",  "worker",  "worth",  "wrongful",  "years",  "Yes",  "you",  "your"]



# ============================================================
# BUILD REPLACEMENT DICTIONARY
# ============================================================

def build_replacement_data(user_exclude_words=None):

    # Start with the original built-in exclusion list.
    combined_exclude_list_all = list(exclude_list_all)

    # Add words entered by the user for this processing operation.
    if user_exclude_words:
        combined_exclude_list_all.extend(user_exclude_words)

    # Remove duplicates while preserving order.
    combined_exclude_list_all = list(
        dict.fromkeys(combined_exclude_list_all)
    )

    # Same behavior as before:
    # only words longer than 2 characters are excluded.
    exclude_list = [
        item
        for item in combined_exclude_list_all
        if len(item) > 0
    ]

    exclude_list_dict = dict(
        zip(
            exclude_list,
            exclude_list
        )
    )

    # Start with the normal Krutidev -> Unicode replacements.
    replacements = dict(
        zip(
            myos,
            myts
        )
    )

    # Add exclusions.
    # This means excluded words map to themselves.
    replacements.update(
        exclude_list_dict
    )

    replacement_pattern, normalized_replacements = (
        compile_replacement_regex(
            replacements
        )
    )

    return replacement_pattern, normalized_replacements


# ============================================================
# PRODUCTION-SAFE ODT PROCESSOR
# ============================================================

def process_odt(
    input_bytes: bytes,
    normalized_replacements,
    replacement_pattern
) -> bytes:

    """
    Process an ODT entirely in memory.

    The original ODT is never uploaded to S3 and no permanent
    file is created on the server.

    The resulting ODT preserves the important ODT ZIP
    requirement that the 'mimetype' entry is first and
    uncompressed.
    """

    input_buffer = BytesIO(
        input_bytes
    )

    output_buffer = BytesIO()


    # --------------------------------------------------------
    # Open original ODT
    # --------------------------------------------------------

    with zipfile.ZipFile(
        input_buffer,
        "r"
    ) as zip_in:

        names = zip_in.namelist()


        # ----------------------------------------------------
        # Basic ODT validation
        # ----------------------------------------------------

        if "mimetype" not in names:

            raise ValueError(
                "This does not appear to be a valid ODT file: "
                "mimetype entry is missing."
            )


        if "content.xml" not in names:

            raise ValueError(
                "This does not appear to be a valid ODT file: "
                "content.xml is missing."
            )


        # ----------------------------------------------------
        # Read mimetype
        # ----------------------------------------------------

        mimetype_data = zip_in.read(
            "mimetype"
        )


        expected_mimetype = (
            b"application/vnd.oasis.opendocument.text"
        )


        if mimetype_data != expected_mimetype:

            raise ValueError(
                "The uploaded file is not an ODT text document."
            )


        # ----------------------------------------------------
        # Create output ZIP
        # ----------------------------------------------------

        with zipfile.ZipFile(
            output_buffer,
            "w"
        ) as zip_out:


            # =================================================
            # VERY IMPORTANT:
            #
            # ODT requires mimetype to be the first entry and
            # it must not be compressed.
            # =================================================

            mimetype_info = zipfile.ZipInfo(
                "mimetype"
            )

            mimetype_info.date_time = (
                1980,
                1,
                1,
                0,
                0,
                0
            )

            mimetype_info.compress_type = (
                zipfile.ZIP_STORED
            )

            mimetype_info.create_system = 3

            zip_out.writestr(
                mimetype_info,
                mimetype_data
            )


            # =================================================
            # Copy remaining files
            # =================================================

            for info in zip_in.infolist():

                filename = info.filename


                # mimetype has already been written.
                if filename == "mimetype":
                    continue


                data = zip_in.read(
                    filename
                )


                # ---------------------------------------------
                # Modify content.xml
                # ---------------------------------------------

                if filename == "content.xml":

                    try:

                        root = ET.fromstring(
                            data
                        )

                    except Exception as e:

                        raise ValueError(
                            f"Unable to parse content.xml: {e}"
                        )


                    # Apply your replacement processing.
                    process_node(
                        root,
                        normalized_replacements,
                        replacement_pattern
                    )


                    # Convert XML tree back to bytes.

                    data = ET.tostring(
                        root,
                        encoding="utf-8",
                        xml_declaration=True
                    )


                # ---------------------------------------------
                # Preserve the original ZIP metadata where
                # possible.
                # ---------------------------------------------

                new_info = zipfile.ZipInfo(
                    filename
                )

                new_info.date_time = (
                    info.date_time
                )

                new_info.comment = (
                    info.comment
                )

                new_info.extra = (
                    info.extra
                )

                new_info.internal_attr = (
                    info.internal_attr
                )

                new_info.external_attr = (
                    info.external_attr
                )

                new_info.create_system = (
                    info.create_system
                )

                new_info.create_version = (
                    info.create_version
                )

                new_info.extract_version = (
                    info.extract_version
                )

                new_info.flag_bits = (
                    info.flag_bits
                )


                # The mimetype is handled above.
                #
                # All other files can be compressed.

                new_info.compress_type = (
                    zipfile.ZIP_DEFLATED
                )


                zip_out.writestr(
                    new_info,
                    data
                )


    # --------------------------------------------------------
    # Return the resulting ODT bytes
    # --------------------------------------------------------

    output_buffer.seek(0)

    return output_buffer.getvalue()


# ============================================================
# STREAMLIT USER INTERFACE
# ============================================================

st.title(
    "Krutidev to Unicode Converter"
)


st.write(
    "Upload only Libreoffice document to process it. Microsoft Word (.doc) file not allowed"
)


st.subheader(
    "Words to exclude from conversion"
)

user_exclude_text = st.text_area(
    "Enter words separated by spaces",
    height=120,
    placeholder="Example: law and order"
)


uploaded_file = st.file_uploader(
    "Select an ODT file",
    type=["odt"],
    accept_multiple_files=False
)


if uploaded_file is not None:

    st.info(
        f"Selected file: {uploaded_file.name}"
    )


    if st.button(
        "Process ODT",
        type="primary",
        use_container_width=True
    ):

        try:

            # -----------------------------------------------
            # Read uploaded file directly into memory.
            # -----------------------------------------------

            input_bytes = (
                uploaded_file.getvalue()
            )


            # -----------------------------------------------
            # Process
            # -----------------------------------------------

            with st.spinner(
                "Processing document..."
            ):

                # -----------------------------------------------
                # Read user's custom exclusion words.
                # -----------------------------------------------
                user_exclude_words = user_exclude_text.split()
                
                # -----------------------------------------------
                # Build replacement data using the built-in
                # exclusions plus the user's exclusions.
                # -----------------------------------------------

                replacement_pattern, normalized_replacements = (
                    build_replacement_data(
                        user_exclude_words
                    )
                )

                # -----------------------------------------------
                # Process
                # -----------------------------------------------

                output_bytes = process_odt(
                    input_bytes,
                    normalized_replacements,
                    replacement_pattern
                )


            # -----------------------------------------------
            # Generate output filename
            # -----------------------------------------------

            original_name = (
                uploaded_file.name
            )


            if original_name.lower().endswith(
                ".odt"
            ):

                output_name = (
                    original_name[:-4]
                    + "_modified.odt"
                )

            else:

                output_name = (
                    original_name
                    + "_modified.odt"
                )


            # -----------------------------------------------
            # Store result in session state.
            #
            # This keeps the result available if Streamlit
            # reruns the script after a button interaction.
            # -----------------------------------------------

            st.session_state[
                "processed_odt"
            ] = output_bytes

            st.session_state[
                "processed_filename"
            ] = output_name


            st.success(
                "ODT processed successfully."
            )


        except Exception as e:

            st.error(
                f"Processing failed: {e}"
            )


# ============================================================
# DOWNLOAD
# ============================================================

if (
    "processed_odt"
    in st.session_state
):

    st.download_button(
        label="⬇️ Download Modified ODT",
        data=st.session_state[
            "processed_odt"
        ],
        file_name=st.session_state[
            "processed_filename"
        ],
        mime=(
            "application/vnd.oasis.opendocument.text"
        ),
        type="primary",
        use_container_width=True
    )

