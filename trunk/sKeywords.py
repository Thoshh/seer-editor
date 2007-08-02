#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#    Distributed under the terms of the GPL (GNU Public License)
#
#    Seer is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#Keywords

import keyword, string
import wx.stc
from sProperty import *

def GetKeyWords(number):
    if number == 0:
        return string.join(keyword.kwlist)
    elif number == 1:
        return "".join(GetCPPKeywords())
    elif number == 2:
        return "".join(GetHTMLKeyWords())
    return ""

def GetLexer(number):
    if number == 0:
        return wx.stc.STC_LEX_PYTHON
    elif number == 1:
        return wx.stc.STC_LEX_CPP
    elif number == 2:
        return wx.stc.STC_LEX_HTML
    return wx.stc.STC_LEX_NULL

def GetCPPKeywords():
    return ["asm ", "auto ", "bool ", "break ", "case ", "catch ", "char ", "class ", "const ", "const_cast ", "continue ", "default ", "delete ", "do ", "double ", "dynamic_cast ", "else ", "enum ", "explicit ", "export ", "extern ", "false ", "float ", "for ", "friend ", "goto ", "if ", "inline ", "int ", "long ", "mutable ", "namespace ", "new ", "operator ", "private ", "protected ", "public ", "register ", "reinterpret_cast ", "return ", "short ", "signed ", "sizeof ", "static ", "static_cast ", "struct ", "switch ", "template ", "this ", "throw ", "true ", "try ", "typedef ", "typeid ", "typename ", "union ", "unsigned ", "using ", "virtual ", "void ", "volatile ", "wchar_t ", "whileasm ", "auto ", "bool ", "break ", "case ", "catch ", "char ", "class ", "const ", "const_cast ", "continue ", "default ", "delete ", "do ", "double ", "dynamic_cast ", "else ", "enum ", "explicit ", "export ", "extern ", "false ", "float ", "for ", "friend ", "goto ", "if ", "inline ", "int ", "long ", "mutable ", "namespace ", "new ", "operator ", "private ", "protected ", "public ", "register ", "reinterpret_cast ", "return ", "short ", "signed ", "sizeof ", "static ", "static_cast ", "struct ", "switch ", "template ", "this ", "throw ", "true ", "try ", "typedef ", "typeid ", "typename ", "union ", "unsigned ", "using ", "virtual ", "void ", "volatile ", "wchar_t ", "while "]

def GetHTMLKeyWords():
    return ["a ", "abbr ", "acronym ", "address ", "applet ", "area ", "b ", "base ", "basefont ", "bdo ", "big ", "blockquote ", "body ", "br ", "button ", "caption ", "center ", "cite ", "code ", "col ", "colgroup ", "dd ", "del ", "dfn ", "dir ", "div ", "dl ", "dt ", "em ", "fieldset ", "font ", "form ", "frame ", "frameset ", "h1 ", "h2 ", "h3 ", "h4 ", "h5 ", "h6 ", "head ", "hr ", "html ", "i ", "iframe ", "img ", "input ", "ins ", "isindex ", "kbd ", "label ", "legend ", "li ", "link ", "map ", "menu ", "meta ", "noframes ", "noscript ", "object ", "ol ", "optgroup ", "option ", "p ", "param ", "pre ", "q ", "s ", "samp ", "script ", "select ", "small ", "span ", "strike ", "strong ", "style ", "sub ", "sup ", "table ", "tbody ", "td ", "textarea ", "tfoot ", "th ", "thead ", "title ", "tr ", "tt ", "u ", "ul ", "var ", "xml ", "xmlns ", "abbr ", "accept-charset ", "accept ", "accesskey ", "action ", "align ", "alink ", "alt ", "archive ", "axis ", "background ", "bgcolor ", "border ", "cellpadding ", "cellspacing ", "char ", "charoff ", "charset ", "checked ", "cite ", "class ", "classid ", "clear ", "codebase ", "codetype ", "color ", "cols ", "colspan ", "compact ", "content ", "coords ", "data ", "datafld ", "dataformatas ", "datapagesize ", "datasrc ", "datetime ", "declare ", "defer ", "dir ", "disabled ", "enctype ", "event ", "face ", "for ", "frame ", "frameborder ", "headers ", "height ", "href ", "hreflang ", "hspace ", "http-equiv ", "id ", "ismap ", "label ", "lang ", "language ", "leftmargin ", "link ", "longdesc ", "marginwidth ", "marginheight ", "maxlength ", "media ", "method ", "multiple ", "name ", "nohref ", "noresize ", "noshade ", "nowrap ", "object ", "onblur ", "onchange ", "onclick ", "ondblclick ", "onfocus ", "onkeydown ", "onkeypress ", "onkeyup ", "onload ", "onmousedown ", "onmousemove ", "onmouseover ", "onmouseout ", "onmouseup ", "onreset ", "onselect ", "onsubmit ", "onunload ", "profile ", "prompt ", "readonly ", "rel ", "rev ", "rows ", "rowspan ", "rules ", "scheme ", "scope ", "selected ", "shape ", "size ", "span ", "src ", "standby ", "start ", "style ", "summary ", "tabindex ", "target ", "text ", "title ", "topmargin ", "type ", "usemap ", "valign ", "value ", "valuetype ", "version ", "vlink ", "vspace ", "width ", "text ", "password ", "checkbox ", "radio ", "submit ", "reset ", "file ", "hidden ", "image ", "public ", "!doctype ", "dtml-var ", "dtml-if ", "dtml-unless ", "dtml-in ", "dtml-with ", "dtml-let ", "dtml-call ", "dtml-raise ", "dtml-try ", "dtml-comment ", "dtml-tree "]
    
def GetRubyKeywords():
    return ["__FILE__ ", " __LINE__ ", "alias ", "and ", "BEGIN ", "begin ", "break ", "case ", "class ", "def ", "defined? ", "do ", "else ", "END ", "end ", "ensure ", "elsif ", "false ", "for ", "if ", "in ", "module ", "next ", "nil ", "not ", "or ", "redo ", "retry ", "retry ", "return ", "self ", "super ", "then ", "true ", "undef ", "unless ",  "until ", "when ", "while ", "yield "]
    
def GetFortranKeywords():
    return ["access ", "action ", "advance ",  "allocatable ", "allocate ", "apostrophe ", "assign ", "assignment ", "associate ", "asynchronous ", "backspace ", "bind ", "blank ", "blockdata ", "call ", "case ", "character ", "class ", "close ", "common ", "complex ", "contains ", "continue ",  "cycle ",  "data ", "deallocate ", "decimal ", "delim ", "default ", "dimension ", "direct ", "do ", "dowhile ", "double ", "doubleprecision ", "else",  "elseif ", "elsewhere ", "encoding ", "end ", "endassociate ", "endblockdata ", "enddo ", "endfile ", "endforall ", "endfunction ", "endif ", "endinterface ", "endmodule ", "endprogram ", "endselect ", "endsubroutine ", "endtype ", "endwhere ", "entry ", "eor ", "equivalence ", "err ", "errmsg ", "exist ", "exit ", "external ", "file ", "flush ", "fmt ", "forall ", "form ", "format ", "formatted ", "function ", "go ", "goto ", "id ", "if ", "implicit ", "in ", "include ", "inout ", "integer ", "inquire ", "intent ", "interface ", "intrinsic ", "iomsg ", "iolength ", "iostat ", "kind ", "len ", "logical ", "module ", "name ", "named ", "namelist ", "nextrec ", "nml " "none ", "nullify ", "number ", "only ", "open ", "opened ", "operator ", "optional ", "out ", "pad ", "parameter ", "pass ", "pause ", "pending ", "pointer ", "pos ", "position ", "precision " "print", "private ", "program ", "protected ", "public ", "quote ", "read ", "readwrite ", "real ", "rec ", "recl ", "recursive ", "result ", "return ", "rewind ", "save ", "select ", "selectcase ", "selecttype ", "sequential ", "sign ", "size ", "stat ", "status ", "stop ", "stream ", "subroutine ", "target ", "then ", "to ", "type ", "unformatted ", "unit ", "use ", "value ", "volatile ", "wait ", "where ", "while ", "write ", "abs ", "achar ", "acos ", "acosd ", "adjustl ", "adjustr ", "aimag ", "aimax0 ", "aimin0 ", "aint ", "ajmax0 ", "ajmin0 ", "akmax0 ", "akmin0 ", "all ", "allocated ", "alog ", "alog10 ", "amax0 ", "amax1 ", "amin0 ", "amin1 ", "amod ", "anint ", "any ", "asin ", "asind ", "associated ", "atan ", "atan2 ", "atan2d ", "atand ", "bitest ", "bitl ", "bitlr ", "bitrl ", "bjtest ", "bit_size ", "bktest ", "break ", "btest ", "cabs ", "ccos ", "cdabs ", "cdcos ", "cdexp ", "cdlog ", "cdsin ", "cdsqrt ", "ceiling ", "cexp ", "char ", "clog ", "cmplx ", "conjg ", "cos ", "cosd ", "cosh ", "count ", "cpu_time ", "cshift ", "csin ", "csqrt ", "dabs ", "dacos ", "dacosd ", "dasin ", "dasind ", "datan ", "datan2 ", "datan2d ", "datand ", "date ", "date_and_time ", "dble ", "dcmplx ", "dconjg ", "dcos ",  "dcosd ", "dcosh ", "dcotan ", "ddim ", "dexp ", "dfloat ", "dflotk ", "dfloti ", "dflotj ", "digits ", "dim ", "dimag ", "dint ", "dlog ", "dlog10 ", "dmax1 ", "dmin1 ", "dmod ", "dnint ", "dot_product ", "dprod ", "dreal ", "dsign ", "dsin ", "dsind ", "dsinh ", "dsqrt ", "dtan ", "dtand ", "dtanh ",  "eoshift ", "epsilon ", "errsns ", "exp ", "exponent ", "float ", "floati ", "floatj ", "floatk ", "floor ", "fraction ", "free ", "huge ", "iabs ", "iachar ", "iand ", "ibclr ", "ibits ", "ibset ", "ichar ", "idate ", "idim ", "idint ", "idnint ", "ieor ", "ifix ", "iiabs ", "iiand ", "iibclr ", "iibits ", "iibset ", "iidim ", "iidint ", "iidnnt ", "iieor ", "iifix ", "iint ", "iior ", "iiqint ", "iiqnnt ", "iishft ", "iishftc ", "iisign ", "ilen ", "imax0 ", "imax1 ", "imin0 ", "imin1 ", "imod ", "index ", "inint ", "inot ", "int ", "int1 ", "int2 ", "int4 ", "int8 ", "iqint ", "iqnint ", "ior ", "ishft ", "ishftc ", "isign ", "isnan ", "izext ", "jiand ", "jibclr ", "jibits ", "jibset ", "jidim ", "jidint ", "jidnnt ", "jieor ", "jifix ", "jint ", "jior ", "jiqint ", "jiqnnt ", "jishft ", "jishftc ", "jisign ", "jmax0 ", "jmax1 ", "jmin0 ", "jmin1 ", "jmod ", "jnint ", "jnot ", "jzext ", "kiabs ", "kiand ", "kibclr ", "kibits ", "kibset ", "kidim ", "kidint ", "kidnnt ", "kieor ", "kifix ", "kind ", "kint ", "kior ", "kishft ", "kishftc ", "kisign ", "kmax0 ", "kmax1 ", "kmin0 ", "kmin1 ", "kmod ", "knint ", "knot ", "kzext ", "lbound ", "leadz ", "len ", "len_trim ", "lenlge ", "lge ", "lgt ", "lle ", "llt ", "log ", "log10 ", "logical lshift",  "malloc matmul ", "max ", "max0 ", "max1 ", "maxexponent ", "maxloc maxval ", "merge ", "min ", "min0 ", "min1 ", "minexponent ", "minloc ", "minval ", "mod ", "modulo ", "mvbits ", "nearest ", "nint ", "not ", "nworkers ", "number_of_processors ", "pack popcnt ", "poppar ", "precision present ", "product ", "radix ", "random ", "random_number ", "random_seed ", "range ", "real ",  "repeat",  "reshape ", "rrspacing ", "rshift ", "scale ", "scan ", "secnds ", "selected_int_kind", "selected_real_kind", "set_exponent ", "shape ", "sign ", "sin ", "sind ", "sinh ", "size ", "sizeof ", "sngl ", "snglq ", "spacing ", "spread ", "sqrt ", "sum ", "system_clock ", "tan ", "tand ", "tanh ", "tiny ", "transfer ", "transpose ", "trim ", "ubound ", "unpack ", "verify "]

def SetSTCStyles(frame, stc, number):
    if number == 0:
        stc.StyleSetSpec(wx.stc.STC_P_CHARACTER, frame.prefs.txtDocumentStyleDictionary[4])
        stc.StyleSetSpec(wx.stc.STC_P_CLASSNAME, frame.prefs.txtDocumentStyleDictionary[5])
        stc.StyleSetSpec(wx.stc.STC_P_COMMENTLINE, frame.prefs.txtDocumentStyleDictionary[6])
        stc.StyleSetSpec(wx.stc.STC_P_COMMENTBLOCK, frame.prefs.txtDocumentStyleDictionary[7])
        stc.StyleSetSpec(wx.stc.STC_P_DEFNAME, frame.prefs.txtDocumentStyleDictionary[8])
        stc.StyleSetSpec(wx.stc.STC_P_WORD, frame.prefs.txtDocumentStyleDictionary[9])
        stc.StyleSetSpec(wx.stc.STC_P_NUMBER, frame.prefs.txtDocumentStyleDictionary[10])
        stc.StyleSetSpec(wx.stc.STC_P_OPERATOR, frame.prefs.txtDocumentStyleDictionary[11])
        stc.StyleSetSpec(wx.stc.STC_P_STRING, frame.prefs.txtDocumentStyleDictionary[12])
        stc.StyleSetSpec(wx.stc.STC_P_STRINGEOL, frame.prefs.txtDocumentStyleDictionary[13])
        stc.StyleSetSpec(wx.stc.STC_P_TRIPLE, frame.prefs.txtDocumentStyleDictionary[14])
        stc.StyleSetSpec(wx.stc.STC_P_TRIPLEDOUBLE, frame.prefs.txtDocumentStyleDictionary[14])
        stc.SetSelForeground(1, getStyleProperty("fore", frame.prefs.txtDocumentStyleDictionary[16]))
        stc.SetSelBackground(1, getStyleProperty("back", frame.prefs.txtDocumentStyleDictionary[16]))
    elif number == 1:
        stc.StyleSetSpec(wx.stc.STC_C_CHARACTER, frame.prefs.txtDocumentStyleDictionary[4])
        stc.StyleSetSpec(wx.stc.STC_C_PREPROCESSOR, frame.prefs.txtDocumentStyleDictionary[5])
        stc.StyleSetSpec(wx.stc.STC_C_COMMENT, frame.prefs.txtDocumentStyleDictionary[6])
        stc.StyleSetSpec(wx.stc.STC_C_COMMENTLINE, frame.prefs.txtDocumentStyleDictionary[6])
        stc.StyleSetSpec(wx.stc.STC_C_COMMENTLINEDOC, frame.prefs.txtDocumentStyleDictionary[6])
        stc.StyleSetSpec(wx.stc.STC_C_COMMENTDOCKEYWORD, frame.prefs.txtDocumentStyleDictionary[6])
        stc.StyleSetSpec(wx.stc.STC_C_COMMENTDOCKEYWORDERROR, frame.prefs.txtDocumentStyleDictionary[6])
        stc.StyleSetSpec(wx.stc.STC_C_COMMENTDOC, frame.prefs.txtDocumentStyleDictionary[6])
        stc.StyleSetSpec(wx.stc.STC_C_VERBATIM, frame.prefs.txtDocumentStyleDictionary[7])
        stc.StyleSetSpec(wx.stc.STC_C_WORD, frame.prefs.txtDocumentStyleDictionary[8])
        stc.StyleSetSpec(wx.stc.STC_C_WORD2, frame.prefs.txtDocumentStyleDictionary[8])
        stc.StyleSetSpec(wx.stc.STC_C_IDENTIFIER, frame.prefs.txtDocumentStyleDictionary[9])
        stc.StyleSetSpec(wx.stc.STC_C_NUMBER, frame.prefs.txtDocumentStyleDictionary[10])
        stc.StyleSetSpec(wx.stc.STC_C_OPERATOR, frame.prefs.txtDocumentStyleDictionary[11])
        stc.StyleSetSpec(wx.stc.STC_C_STRING, frame.prefs.txtDocumentStyleDictionary[12])
        stc.StyleSetSpec(wx.stc.STC_C_STRINGEOL, frame.prefs.txtDocumentStyleDictionary[13])
        stc.StyleSetSpec(wx.stc.STC_C_GLOBALCLASS, frame.prefs.txtDocumentStyleDictionary[14])
        stc.StyleSetSpec(wx.stc.STC_C_REGEX, frame.prefs.txtDocumentStyleDictionary[15])
        stc.StyleSetSpec(wx.stc.STC_C_UUID, frame.prefs.txtDocumentStyleDictionary[16])
        stc.SetSelForeground(1, getStyleProperty("fore", frame.prefs.txtDocumentStyleDictionary[18]))
        stc.SetSelBackground(1, getStyleProperty("back", frame.prefs.txtDocumentStyleDictionary[18]))
    elif number == 2:
        stc.StyleSetSpec(wx.stc.STC_H_TAG, frame.prefs.txtDocumentStyleDictionary[4])
        stc.StyleSetSpec(wx.stc.STC_H_TAGUNKNOWN, frame.prefs.txtDocumentStyleDictionary[5])
        stc.StyleSetSpec(wx.stc.STC_H_ATTRIBUTE, frame.prefs.txtDocumentStyleDictionary[6])
        stc.StyleSetSpec(wx.stc.STC_H_ATTRIBUTEUNKNOWN, frame.prefs.txtDocumentStyleDictionary[7])
        stc.StyleSetSpec(wx.stc.STC_H_NUMBER, frame.prefs.txtDocumentStyleDictionary[8])
        stc.StyleSetSpec(wx.stc.STC_H_DOUBLESTRING, frame.prefs.txtDocumentStyleDictionary[9])
        stc.StyleSetSpec(wx.stc.STC_H_SINGLESTRING, frame.prefs.txtDocumentStyleDictionary[10])
        stc.StyleSetSpec(wx.stc.STC_H_OTHER, frame.prefs.txtDocumentStyleDictionary[10])
        stc.StyleSetSpec(wx.stc.STC_H_COMMENT, frame.prefs.txtDocumentStyleDictionary[11])
        stc.StyleSetSpec(wx.stc.STC_H_XCCOMMENT, frame.prefs.txtDocumentStyleDictionary[11])
        stc.StyleSetSpec(wx.stc.STC_H_ENTITY, frame.prefs.txtDocumentStyleDictionary[12])
        stc.StyleSetSpec(wx.stc.STC_H_TAGEND, frame.prefs.txtDocumentStyleDictionary[13])
        stc.StyleSetSpec(wx.stc.STC_H_XMLSTART, frame.prefs.txtDocumentStyleDictionary[14])
        stc.StyleSetSpec(wx.stc.STC_H_XMLEND, frame.prefs.txtDocumentStyleDictionary[15])
        stc.StyleSetSpec(wx.stc.STC_H_SCRIPT, frame.prefs.txtDocumentStyleDictionary[16])
        stc.StyleSetSpec(wx.stc.STC_H_ASP, frame.prefs.txtDocumentStyleDictionary[16])
        stc.StyleSetSpec(wx.stc.STC_H_ASPAT, frame.prefs.txtDocumentStyleDictionary[16])
        stc.StyleSetSpec(wx.stc.STC_H_VALUE, frame.prefs.txtDocumentStyleDictionary[17])
        stc.StyleSetSpec(wx.stc.STC_H_QUESTION, frame.prefs.txtDocumentStyleDictionary[17])
        stc.SetSelForeground(1, getStyleProperty("fore", frame.prefs.txtDocumentStyleDictionary[19]))
        stc.SetSelBackground(1, getStyleProperty("back", frame.prefs.txtDocumentStyleDictionary[19]))