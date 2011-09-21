(function(window, undefined) {

    var ieWarning = function(cb) {
        var configObj = (typeof(cb) == 'function') ? cb() : {},

        l10n = configObj.localizations,

        imagesStyle = {
            bg: 'transparent url(/static/images/browsers.jpg) no-repeat scroll ',
            background: {
                bgPos: '-185px -93px',
                w: '120px',
                h: '122px'
            },
            ie: {
                bgPos: '8px -86px',
                w: '100px',
                h: '110px'
            },
            ff: {
                bgPos: '-84px -86px',
                w: '100px',
                h: '110px'
            },
            safari: {
                bgPos: '-84px 7px',
                w: '100px',
                h: '110px'
            },
            opera: {
                bgPos: '8px 7px',
                w: '100px',
                h: '110px'
            },
            chrome: {
                bgPos: '-174px 7px',
                w: '100px',
                h: '110px'
            }
        },

        _html = {
            d: document.createElement('div'),
            l: document.createElement('div'),
            h: document.createElement('h1'),
            p1: document.createElement('p'),
            p2: document.createElement('p'),
            ul: document.createElement('ul'),
            li: {
                ie: document.createElement('li'),
                ff: document.createElement('li'),
                safari: document.createElement('li'),
                opera: document.createElement('li'),
                chrome: document.createElement('li')
            },
            ico: {
                ie: document.createElement('div'),
                ff: document.createElement('div'),
                safari: document.createElement('div'),
                opera: document.createElement('div'),
                chrome: document.createElement('div')
            },
            lit: {
                ie: document.createElement('div'),
                ff: document.createElement('div'),
                safari: document.createElement('div'),
                opera: document.createElement('div'),
                chrome: document.createElement('div')
            }
        },
        _width = document.documentElement.clientWidth,
        _height = document.documentElement.clientHeight;

        //setup document
        (function() {
            document.body.appendChild(_html.l);
            document.body.appendChild(_html.d);
            //left these attributes so someone can target the rest of the message with custom CSS
            _html.d.appendChild(_html.h);
            _html.d.appendChild(_html.p1);
            _html.d.appendChild(_html.p2);
            _html.d.appendChild(_html.ul);
            for (var key in _html.li) {
                if (_html.li.hasOwnProperty(key)) {
                    _html.ul.appendChild(_html.li[key]);
                    _html.li[key].appendChild(_html.ico[key]);
                    _html.li[key].appendChild(_html.lit[key]);
                }
            }
        })();

        //set up lights out effect
        (function() {
            _html.l.setAttribute('id','lightsOut');
            _html.l.style.zIndex = 99998;
            _html.l.style.width =  _width+"px";
            _html.l.style.height = _height+"px";
            _html.l.style.position = "absolute";
            _html.l.style.top = "0px";
            _html.l.style.left = "0px";
            _html.l.style.filter = "alpha(opacity=50)";
            _html.l.style.background = "#fff";
        })();

        //setup ie6warning box
        (function() {
            var _ddw = 650,
                _ddh = 260;
            _html.d.setAttribute('id','ie6Warning');
            _html.d.style.zIndex = 99999;
            _html.d.style.width = _ddw+"px";
            _html.d.style.height = _ddh+"px";
            _html.d.style.position = "absolute";
            _html.d.style.top = ((_height-_ddh)/2)+"px";
            _html.d.style.left = ((_width-_ddw)/2)+"px";
            _html.d.style.padding = "20px";
            _html.d.style.background = "#fff";
            _html.d.style.border = "1px solid #ccc";
            _html.d.style.fontFamily = "'Lucida Grande','Lucida Sans Unicode',Arial,Verdana,sans-serif";
            _html.d.style.listStyleType = "none";
            _html.d.style.color = "#4F4F4F";
            _html.d.style.fontSize = "12px";
        })();

        //setup header messaging
        (function() {
            _html.h.appendChild(document.createTextNode(l10n.msg1));
            _html.h.style.display = "block";
            _html.h.style.fontSize = "1.3em";
            _html.h.style.marginBottom = "0.5em";
            _html.h.style.color = "#333";
            _html.h.style.fontFamily = "Helvetica,Arial,sans-serif";
            _html.h.style.fontWeight = "bold";
            _html.p1.appendChild(document.createTextNode(l10n.msg2));
            _html.p1.style.marginBottom = "1em";
            _html.p2.appendChild(document.createTextNode(l10n.msg3));
            _html.p2.style.marginBottom = "1em";
        })();

        //setup of browser list
        (function() {
            _html.ul.style.listStyleImage = "none";
            _html.ul.style.listStylePosition = "outside";
            _html.ul.style.listStyleType = "none";
            _html.ul.style.margin = "0px auto";
            _html.ul.style.padding = "5px";

            for (var key in _html.li) {
                var keyS;
                if (_html.li.hasOwnProperty(key)) {
                    keyS = _html.li[key].style;
                    keyS.background = imagesStyle.bg + imagesStyle.background.bgPos;
                    keyS.width = imagesStyle.background.w;
                    keyS.height = imagesStyle.background.h;
                    keyS.cursor = "pointer";
                    keyS.styleFloat = keyS.cssFloat = "left";
                    keyS.margin = "0 10px 10px 0";
                    //wrapping with a closure to emulate a real local var
                    _html.li[key].onclick = (function(){ var akey = key; return function() { window.location = l10n.url[akey] } } )();
                }

                if (_html.ico.hasOwnProperty(key)) {
                    keyS = _html.ico[key].style;
                    keyS.width = "100px";
                    keyS.height = "100px";
                    keyS.margin = "1px auto";
                    keyS.background = imagesStyle.bg + imagesStyle[key].bgPos;
                }

                if (_html.lit.hasOwnProperty(key)) {
                    keyS = _html.lit[key].style;
                    keyS.color = "#808080";
                    keyS.fontSize = "10px";
                    keyS.width = "118px";
                    keyS.height = "18px";
                    keyS.lineHeight = "17px";
                    keyS.margin = "1px auto";
                    keyS.textAlign = "center";
                    _html.lit[key].appendChild(document.createTextNode(l10n.br[key]));
                }
            }
            //removing left margin on last element
            _html.li.chrome.style.margin = "0 0 10px";
        })();
    };

    //set it to global namesapce
    window.ie6Warning = ieWarning;
})(window);
