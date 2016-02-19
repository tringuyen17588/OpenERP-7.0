# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import time
from PIL import Image
import zbar

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    _columns = {
        'is_title': fields.boolean('Is title'),
    }
    _defaults = {
        'is_title': False,
    }
    def onchange_title(self, cr, uid, ids, title):
        
        return {'value': {'product_id': 0,
                          'product_uom_qty': 0,
                          'price_unit': 0}}
    
account_invoice_line()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'is_dhl': fields.boolean('Is DHL'),
        'dhl_id': fields.many2one('account.invoice', 'DHL Invoice'),
        'inv_ids': fields.many2many('account.invoice', 'dhl_invoice_rel', 'dhl_id', 'inv_id', 'Delivered For Invoices'),
        'youtube_link': fields.binary("Image",
            help="This field holds the image used as image for the product, limited to 1024x1024px."), 
        'youtube_show': fields.text('Youtube show'),
        'url_image': fields.char('URL', size=256),
        'result_barcode': fields.char('Barcode Result', size=256),
    }
    _defaults = {
        'is_dhl': False,
    }

    def onchange_url(self, cr, uid, ids, url):
        if not url:
            return {'value': {}}
        else:
            pil = Image.open('%s'%url).convert('L')
            width, height = pil.size
            raw = pil.tostring()
            image = zbar.Image(width, height, 'Y800', raw)
            scanner = zbar.ImageScanner()
            scanner.scan(image)
            result = ''
            for s in image:
                result = s.data
            return {'value': {'result_barcode': str(result)}}
        return {'value': {}}
    
    def check_html(self, cr, uid, ids, context={}):
        for record in self.browse(cr, uid, ids):
            print record.youtube_show
        return 1
    
    def onchange_link(self, cr, uid, ids, link):
        
        if not link:
            return {'value': {'youtube_show': ''}}
        else:
            content = ''' 
<html>
 <head>
  <link rel="stylesheet" type="text/css" href="./css/style.css" /> 
  <script>
    var qrcode1 = function() {
    var qrcode = function(typeNumber, errorCorrectLevel) {

        var PAD0 = 0xEC;
        var PAD1 = 0x11;

        var _typeNumber = typeNumber;
        var _errorCorrectLevel = QRErrorCorrectLevel[errorCorrectLevel];
        var _modules = null;
        var _moduleCount = 0;
        var _dataCache = null;
        var _dataList = new Array();

        var _this = {};

        var makeImpl = function(test, maskPattern) {

            _moduleCount = _typeNumber * 4 + 17;
            _modules = function(moduleCount) {
                var modules = new Array(moduleCount);
                for (var row = 0; row < moduleCount; row += 1) {
                    modules[row] = new Array(moduleCount);
                    for (var col = 0; col < moduleCount; col += 1) {
                        modules[row][col] = null;
                    }
                }
                return modules;
            }(_moduleCount);

            setupPositionProbePattern(0, 0);
            setupPositionProbePattern(_moduleCount - 7, 0);
            setupPositionProbePattern(0, _moduleCount - 7);
            setupPositionAdjustPattern();
            setupTimingPattern();
            setupTypeInfo(test, maskPattern);

            if (_typeNumber >= 7) {
                setupTypeNumber(test);
            }

            if (_dataCache == null) {
                _dataCache = createData(_typeNumber, _errorCorrectLevel, _dataList);
            }

            mapData(_dataCache, maskPattern);
        };

        var setupPositionProbePattern = function(row, col) {

            for (var r = -1; r <= 7; r += 1) {

                if (row + r <= -1 || _moduleCount <= row + r) continue;

                for (var c = -1; c <= 7; c += 1) {

                    if (col + c <= -1 || _moduleCount <= col + c) continue;

                    if ( (0 <= r && r <= 6 && (c == 0 || c == 6) )
                            || (0 <= c && c <= 6 && (r == 0 || r == 6) )
                            || (2 <= r && r <= 4 && 2 <= c && c <= 4) ) {
                        _modules[row + r][col + c] = true;
                    } else {
                        _modules[row + r][col + c] = false;
                    }
                }
            }
        };

        var getBestMaskPattern = function() {

            var minLostPoint = 0;
            var pattern = 0;

            for (var i = 0; i < 8; i += 1) {

                makeImpl(true, i);

                var lostPoint = QRUtil.getLostPoint(_this);

                if (i == 0 || minLostPoint > lostPoint) {
                    minLostPoint = lostPoint;
                    pattern = i;
                }
            }

            return pattern;
        };

        var setupTimingPattern = function() {

            for (var r = 8; r < _moduleCount - 8; r += 1) {
                if (_modules[r][6] != null) {
                    continue;
                }
                _modules[r][6] = (r % 2 == 0);
            }

            for (var c = 8; c < _moduleCount - 8; c += 1) {
                if (_modules[6][c] != null) {
                    continue;
                }
                _modules[6][c] = (c % 2 == 0);
            }
        };

        var setupPositionAdjustPattern = function() {

            var pos = QRUtil.getPatternPosition(_typeNumber);

            for (var i = 0; i < pos.length; i += 1) {

                for (var j = 0; j < pos.length; j += 1) {

                    var row = pos[i];
                    var col = pos[j];

                    if (_modules[row][col] != null) {
                        continue;
                    }

                    for (var r = -2; r <= 2; r += 1) {

                        for (var c = -2; c <= 2; c += 1) {

                            if (r == -2 || r == 2 || c == -2 || c == 2
                                    || (r == 0 && c == 0) ) {
                                _modules[row + r][col + c] = true;
                            } else {
                                _modules[row + r][col + c] = false;
                            }
                        }
                    }
                }
            }
        };

        var setupTypeNumber = function(test) {

            var bits = QRUtil.getBCHTypeNumber(_typeNumber);

            for (var i = 0; i < 18; i += 1) {
                var mod = (!test && ( (bits >> i) & 1) == 1);
                _modules[Math.floor(i / 3)][i % 3 + _moduleCount - 8 - 3] = mod;
            }

            for (var i = 0; i < 18; i += 1) {
                var mod = (!test && ( (bits >> i) & 1) == 1);
                _modules[i % 3 + _moduleCount - 8 - 3][Math.floor(i / 3)] = mod;
            }
        };

        var setupTypeInfo = function(test, maskPattern) {

            var data = (_errorCorrectLevel << 3) | maskPattern;
            var bits = QRUtil.getBCHTypeInfo(data);

            // vertical
            for (var i = 0; i < 15; i += 1) {

                var mod = (!test && ( (bits >> i) & 1) == 1);

                if (i < 6) {
                    _modules[i][8] = mod;
                } else if (i < 8) {
                    _modules[i + 1][8] = mod;
                } else {
                    _modules[_moduleCount - 15 + i][8] = mod;
                }
            }

            // horizontal
            for (var i = 0; i < 15; i += 1) {

                var mod = (!test && ( (bits >> i) & 1) == 1);

                if (i < 8) {
                    _modules[8][_moduleCount - i - 1] = mod;
                } else if (i < 9) {
                    _modules[8][15 - i - 1 + 1] = mod;
                } else {
                    _modules[8][15 - i - 1] = mod;
                }
            }

            // fixed module
            _modules[_moduleCount - 8][8] = (!test);
        };

        var mapData = function(data, maskPattern) {

            var inc = -1;
            var row = _moduleCount - 1;
            var bitIndex = 7;
            var byteIndex = 0;
            var maskFunc = QRUtil.getMaskFunction(maskPattern);

            for (var col = _moduleCount - 1; col > 0; col -= 2) {

                if (col == 6) col -= 1;

                while (true) {

                    for (var c = 0; c < 2; c += 1) {

                        if (_modules[row][col - c] == null) {

                            var dark = false;

                            if (byteIndex < data.length) {
                                dark = ( ( (data[byteIndex] >>> bitIndex) & 1) == 1);
                            }

                            var mask = maskFunc(row, col - c);

                            if (mask) {
                                dark = !dark;
                            }

                            _modules[row][col - c] = dark;
                            bitIndex -= 1;

                            if (bitIndex == -1) {
                                byteIndex += 1;
                                bitIndex = 7;
                            }
                        }
                    }

                    row += inc;

                    if (row < 0 || _moduleCount <= row) {
                        row -= inc;
                        inc = -inc;
                        break;
                    }
                }
            }
        };

        var createBytes = function(buffer, rsBlocks) {

            var offset = 0;

            var maxDcCount = 0;
            var maxEcCount = 0;

            var dcdata = new Array(rsBlocks.length);
            var ecdata = new Array(rsBlocks.length);

            for (var r = 0; r < rsBlocks.length; r += 1) {

                var dcCount = rsBlocks[r].dataCount;
                var ecCount = rsBlocks[r].totalCount - dcCount;

                maxDcCount = Math.max(maxDcCount, dcCount);
                maxEcCount = Math.max(maxEcCount, ecCount);

                dcdata[r] = new Array(dcCount);

                for (var i = 0; i < dcdata[r].length; i += 1) {
                    dcdata[r][i] = 0xff & buffer.getBuffer()[i + offset];
                }
                offset += dcCount;

                var rsPoly = QRUtil.getErrorCorrectPolynomial(ecCount);
                var rawPoly = qrPolynomial(dcdata[r], rsPoly.getLength() - 1);

                var modPoly = rawPoly.mod(rsPoly);
                ecdata[r] = new Array(rsPoly.getLength() - 1);
                for (var i = 0; i < ecdata[r].length; i += 1) {
                    var modIndex = i + modPoly.getLength() - ecdata[r].length;
                    ecdata[r][i] = (modIndex >= 0)? modPoly.getAt(modIndex) : 0;
                }
            }

            var totalCodeCount = 0;
            for (var i = 0; i < rsBlocks.length; i += 1) {
                totalCodeCount += rsBlocks[i].totalCount;
            }

            var data = new Array(totalCodeCount);
            var index = 0;

            for (var i = 0; i < maxDcCount; i += 1) {
                for (var r = 0; r < rsBlocks.length; r += 1) {
                    if (i < dcdata[r].length) {
                        data[index] = dcdata[r][i];
                        index += 1;
                    }
                }
            }

            for (var i = 0; i < maxEcCount; i += 1) {
                for (var r = 0; r < rsBlocks.length; r += 1) {
                    if (i < ecdata[r].length) {
                        data[index] = ecdata[r][i];
                        index += 1;
                    }
                }
            }

            return data;
        };

        var createData = function(typeNumber, errorCorrectLevel, dataList) {

            var rsBlocks = QRRSBlock.getRSBlocks(typeNumber, errorCorrectLevel);

            var buffer = qrBitBuffer();

            for (var i = 0; i < dataList.length; i += 1) {
                var data = dataList[i];
                buffer.put(data.getMode(), 4);
                buffer.put(data.getLength(), QRUtil.getLengthInBits(data.getMode(), typeNumber) );
                data.write(buffer);
            }

            // calc num max data.
            var totalDataCount = 0;
            for (var i = 0; i < rsBlocks.length; i += 1) {
                totalDataCount += rsBlocks[i].dataCount;
            }

            if (buffer.getLengthInBits() > totalDataCount * 8) {
                throw new Error('code length overflow. ('
                    + buffer.getLengthInBits()
                    + '>'
                    + totalDataCount * 8
                    + ')');
            }

            // end code
            if (buffer.getLengthInBits() + 4 <= totalDataCount * 8) {
                buffer.put(0, 4);
            }

            // padding
            while (buffer.getLengthInBits() % 8 != 0) {
                buffer.putBit(false);
            }

            // padding
            while (true) {

                if (buffer.getLengthInBits() >= totalDataCount * 8) {
                    break;
                }
                buffer.put(PAD0, 8);

                if (buffer.getLengthInBits() >= totalDataCount * 8) {
                    break;
                }
                buffer.put(PAD1, 8);
            }

            return createBytes(buffer, rsBlocks);
        };

        _this.addData = function(data) {
            var newData = qr8BitByte(data);
            _dataList.push(newData);
            _dataCache = null;
        };

        _this.isDark = function(row, col) {
            if (row < 0 || _moduleCount <= row || col < 0 || _moduleCount <= col) {
                throw new Error(row + ',' + col);
            }
            return _modules[row][col];
        };

        _this.getModuleCount = function() {
            return _moduleCount;
        };

        _this.make = function() {
            makeImpl(false, getBestMaskPattern() );
        };

        _this.createTableTag = function(cellSize, margin) {

            cellSize = cellSize || 2;
            margin = (typeof margin == 'undefined')? cellSize * 4 : margin;

            var qrHtml = '';

            qrHtml += '<table style="';
            qrHtml += ' border-width: 0px; border-style: none;';
            qrHtml += ' border-collapse: collapse;';
            qrHtml += ' padding: 0px; margin: ' + margin + 'px;';
            qrHtml += '">';
            qrHtml += '<tbody>';

            for (var r = 0; r < _this.getModuleCount(); r += 1) {

                qrHtml += '<tr>';

                for (var c = 0; c < _this.getModuleCount(); c += 1) {
                    qrHtml += '<td style="';
                    qrHtml += ' border-width: 0px; border-style: none;';
                    qrHtml += ' border-collapse: collapse;';
                    qrHtml += ' padding: 0px; margin: 0px;';
                    qrHtml += ' width: ' + cellSize + 'px;';
                    qrHtml += ' height: ' + cellSize + 'px;';
                    qrHtml += ' background-color: ';
                    qrHtml += _this.isDark(r, c)? '#000000' : '#ffffff';
                    qrHtml += ';';
                    qrHtml += '"/>';
                }

                qrHtml += '</tr>';
            }

            qrHtml += '</tbody>';
            qrHtml += '</table>';

            return qrHtml;
        };

        _this.createImgTag = function(cellSize, margin) {

            cellSize = cellSize || 2;
            margin = (typeof margin == 'undefined')? cellSize * 4 : margin;

            var size = _this.getModuleCount() * cellSize + margin * 2;
            var min = margin;
            var max = size - margin;

            return createImgTag(size, size, function(x, y) {
                if (min <= x && x < max && min <= y && y < max) {
                    var c = Math.floor( (x - min) / cellSize);
                    var r = Math.floor( (y - min) / cellSize);
                    return _this.isDark(r, c)? 0 : 1;
                } else {
                    return 1;
                }
            } );
        };

        return _this;
    };

    //---------------------------------------------------------------------
    // qrcode.stringToBytes
    //---------------------------------------------------------------------

    qrcode.stringToBytes = function(s) {
        var bytes = new Array();
        for (var i = 0; i < s.length; i += 1) {
            var c = s.charCodeAt(i);
            bytes.push(c & 0xff);
        }
        return bytes;
    };

    //---------------------------------------------------------------------
    // qrcode.createStringToBytes
    //---------------------------------------------------------------------

    /**
     * @param unicodeData base64 string of byte array.
     * [16bit Unicode],[16bit Bytes], ...
     * @param numChars
     */
    qrcode.createStringToBytes = function(unicodeData, numChars) {

        // create conversion map.

        var unicodeMap = function() {

            var bin = base64DecodeInputStream(unicodeData);
            var read = function() {
                var b = bin.read();
                if (b == -1) throw new Error();
                return b;
            };

            var count = 0;
            var unicodeMap = {};
            while (true) {
                var b0 = bin.read();
                if (b0 == -1) break;
                var b1 = read();
                var b2 = read();
                var b3 = read();
                var k = String.fromCharCode( (b0 << 8) | b1);
                var v = (b2 << 8) | b3;
                unicodeMap[k] = v;
                count += 1;
            }
            if (count != numChars) {
                throw new Error(count + ' != ' + numChars);
            }

            return unicodeMap;
        }();

        var unknownChar = '?'.charCodeAt(0);

        return function(s) {
            var bytes = new Array();
            for (var i = 0; i < s.length; i += 1) {
                var c = s.charCodeAt(i);
                if (c < 128) {
                    bytes.push(c);
                } else {
                    var b = unicodeMap[s.charAt(i)];
                    if (typeof b == 'number') {
                        if ( (b & 0xff) == b) {
                            // 1byte
                            bytes.push(b);
                        } else {
                            // 2bytes
                            bytes.push(b >>> 8);
                            bytes.push(b & 0xff);
                        }
                    } else {
                        bytes.push(unknownChar);
                    }
                }
            }
            return bytes;
        };
    };

    //---------------------------------------------------------------------
    // QRMode
    //---------------------------------------------------------------------

    var QRMode = {
        MODE_NUMBER :        1 << 0,
        MODE_ALPHA_NUM :     1 << 1,
        MODE_8BIT_BYTE :     1 << 2,
        MODE_KANJI :        1 << 3
    };

    //---------------------------------------------------------------------
    // QRErrorCorrectLevel
    //---------------------------------------------------------------------

    var QRErrorCorrectLevel = {
        L : 1,
        M : 0,
        Q : 3,
        H : 2
    };

    //---------------------------------------------------------------------
    // QRMaskPattern
    //---------------------------------------------------------------------

    var QRMaskPattern = {
        PATTERN000 : 0,
        PATTERN001 : 1,
        PATTERN010 : 2,
        PATTERN011 : 3,
        PATTERN100 : 4,
        PATTERN101 : 5,
        PATTERN110 : 6,
        PATTERN111 : 7
    };

    //---------------------------------------------------------------------
    // QRUtil
    //---------------------------------------------------------------------

    var QRUtil = function() {

        var PATTERN_POSITION_TABLE = [
            [],
            [6, 18],
            [6, 22],
            [6, 26],
            [6, 30],
            [6, 34],
            [6, 22, 38],
            [6, 24, 42],
            [6, 26, 46],
            [6, 28, 50],
            [6, 30, 54],
            [6, 32, 58],
            [6, 34, 62],
            [6, 26, 46, 66],
            [6, 26, 48, 70],
            [6, 26, 50, 74],
            [6, 30, 54, 78],
            [6, 30, 56, 82],
            [6, 30, 58, 86],
            [6, 34, 62, 90],
            [6, 28, 50, 72, 94],
            [6, 26, 50, 74, 98],
            [6, 30, 54, 78, 102],
            [6, 28, 54, 80, 106],
            [6, 32, 58, 84, 110],
            [6, 30, 58, 86, 114],
            [6, 34, 62, 90, 118],
            [6, 26, 50, 74, 98, 122],
            [6, 30, 54, 78, 102, 126],
            [6, 26, 52, 78, 104, 130],
            [6, 30, 56, 82, 108, 134],
            [6, 34, 60, 86, 112, 138],
            [6, 30, 58, 86, 114, 142],
            [6, 34, 62, 90, 118, 146],
            [6, 30, 54, 78, 102, 126, 150],
            [6, 24, 50, 76, 102, 128, 154],
            [6, 28, 54, 80, 106, 132, 158],
            [6, 32, 58, 84, 110, 136, 162],
            [6, 26, 54, 82, 110, 138, 166],
            [6, 30, 58, 86, 114, 142, 170]
        ];
        var G15 = (1 << 10) | (1 << 8) | (1 << 5) | (1 << 4) | (1 << 2) | (1 << 1) | (1 << 0);
        var G18 = (1 << 12) | (1 << 11) | (1 << 10) | (1 << 9) | (1 << 8) | (1 << 5) | (1 << 2) | (1 << 0);
        var G15_MASK = (1 << 14) | (1 << 12) | (1 << 10) | (1 << 4) | (1 << 1);

        var _this = {};

        var getBCHDigit = function(data) {
            var digit = 0;
            while (data != 0) {
                digit += 1;
                data >>>= 1;
            }
            return digit;
        };

        _this.getBCHTypeInfo = function(data) {
            var d = data << 10;
            while (getBCHDigit(d) - getBCHDigit(G15) >= 0) {
                d ^= (G15 << (getBCHDigit(d) - getBCHDigit(G15) ) );
            }
            return ( (data << 10) | d) ^ G15_MASK;
        };

        _this.getBCHTypeNumber = function(data) {
            var d = data << 12;
            while (getBCHDigit(d) - getBCHDigit(G18) >= 0) {
                d ^= (G18 << (getBCHDigit(d) - getBCHDigit(G18) ) );
            }
            return (data << 12) | d;
        };

        _this.getPatternPosition = function(typeNumber) {
            return PATTERN_POSITION_TABLE[typeNumber - 1];
        };

        _this.getMaskFunction = function(maskPattern) {

            switch (maskPattern) {

            case QRMaskPattern.PATTERN000 :
                return function(i, j) { return (i + j) % 2 == 0; };
            case QRMaskPattern.PATTERN001 :
                return function(i, j) { return i % 2 == 0; };
            case QRMaskPattern.PATTERN010 :
                return function(i, j) { return j % 3 == 0; };
            case QRMaskPattern.PATTERN011 :
                return function(i, j) { return (i + j) % 3 == 0; };
            case QRMaskPattern.PATTERN100 :
                return function(i, j) { return (Math.floor(i / 2) + Math.floor(j / 3) ) % 2 == 0; };
            case QRMaskPattern.PATTERN101 :
                return function(i, j) { return (i * j) % 2 + (i * j) % 3 == 0; };
            case QRMaskPattern.PATTERN110 :
                return function(i, j) { return ( (i * j) % 2 + (i * j) % 3) % 2 == 0; };
            case QRMaskPattern.PATTERN111 :
                return function(i, j) { return ( (i * j) % 3 + (i + j) % 2) % 2 == 0; };

            default :
                throw new Error('bad maskPattern:' + maskPattern);
            }
        };

        _this.getErrorCorrectPolynomial = function(errorCorrectLength) {
            var a = qrPolynomial([1], 0);
            for (var i = 0; i < errorCorrectLength; i += 1) {
                a = a.multiply(qrPolynomial([1, QRMath.gexp(i)], 0) );
            }
            return a;
        };

        _this.getLengthInBits = function(mode, type) {

            if (1 <= type && type < 10) {

                // 1 - 9

                switch(mode) {
                case QRMode.MODE_NUMBER     : return 10;
                case QRMode.MODE_ALPHA_NUM     : return 9;
                case QRMode.MODE_8BIT_BYTE    : return 8;
                case QRMode.MODE_KANJI        : return 8;
                default :
                    throw new Error('mode:' + mode);
                }

            } else if (type < 27) {

                // 10 - 26

                switch(mode) {
                case QRMode.MODE_NUMBER     : return 12;
                case QRMode.MODE_ALPHA_NUM     : return 11;
                case QRMode.MODE_8BIT_BYTE    : return 16;
                case QRMode.MODE_KANJI        : return 10;
                default :
                    throw new Error('mode:' + mode);
                }

            } else if (type < 41) {

                // 27 - 40

                switch(mode) {
                case QRMode.MODE_NUMBER     : return 14;
                case QRMode.MODE_ALPHA_NUM    : return 13;
                case QRMode.MODE_8BIT_BYTE    : return 16;
                case QRMode.MODE_KANJI        : return 12;
                default :
                    throw new Error('mode:' + mode);
                }

            } else {
                throw new Error('type:' + type);
            }
        };

        _this.getLostPoint = function(qrcode) {

            var moduleCount = qrcode.getModuleCount();

            var lostPoint = 0;

            // LEVEL1

            for (var row = 0; row < moduleCount; row += 1) {
                for (var col = 0; col < moduleCount; col += 1) {

                    var sameCount = 0;
                    var dark = qrcode.isDark(row, col);

                    for (var r = -1; r <= 1; r += 1) {

                        if (row + r < 0 || moduleCount <= row + r) {
                            continue;
                        }

                        for (var c = -1; c <= 1; c += 1) {

                            if (col + c < 0 || moduleCount <= col + c) {
                                continue;
                            }

                            if (r == 0 && c == 0) {
                                continue;
                            }

                            if (dark == qrcode.isDark(row + r, col + c) ) {
                                sameCount += 1;
                            }
                        }
                    }

                    if (sameCount > 5) {
                        lostPoint += (3 + sameCount - 5);
                    }
                }
            };

            // LEVEL2

            for (var row = 0; row < moduleCount - 1; row += 1) {
                for (var col = 0; col < moduleCount - 1; col += 1) {
                    var count = 0;
                    if (qrcode.isDark(row, col) ) count += 1;
                    if (qrcode.isDark(row + 1, col) ) count += 1;
                    if (qrcode.isDark(row, col + 1) ) count += 1;
                    if (qrcode.isDark(row + 1, col + 1) ) count += 1;
                    if (count == 0 || count == 4) {
                        lostPoint += 3;
                    }
                }
            }

            // LEVEL3

            for (var row = 0; row < moduleCount; row += 1) {
                for (var col = 0; col < moduleCount - 6; col += 1) {
                    if (qrcode.isDark(row, col)
                            && !qrcode.isDark(row, col + 1)
                            &&  qrcode.isDark(row, col + 2)
                            &&  qrcode.isDark(row, col + 3)
                            &&  qrcode.isDark(row, col + 4)
                            && !qrcode.isDark(row, col + 5)
                            &&  qrcode.isDark(row, col + 6) ) {
                        lostPoint += 40;
                    }
                }
            }

            for (var col = 0; col < moduleCount; col += 1) {
                for (var row = 0; row < moduleCount - 6; row += 1) {
                    if (qrcode.isDark(row, col)
                            && !qrcode.isDark(row + 1, col)
                            &&  qrcode.isDark(row + 2, col)
                            &&  qrcode.isDark(row + 3, col)
                            &&  qrcode.isDark(row + 4, col)
                            && !qrcode.isDark(row + 5, col)
                            &&  qrcode.isDark(row + 6, col) ) {
                        lostPoint += 40;
                    }
                }
            }

            // LEVEL4

            var darkCount = 0;

            for (var col = 0; col < moduleCount; col += 1) {
                for (var row = 0; row < moduleCount; row += 1) {
                    if (qrcode.isDark(row, col) ) {
                        darkCount += 1;
                    }
                }
            }

            var ratio = Math.abs(100 * darkCount / moduleCount / moduleCount - 50) / 5;
            lostPoint += ratio * 10;

            return lostPoint;
        };

        return _this;
    }();

    //---------------------------------------------------------------------
    // QRMath
    //---------------------------------------------------------------------

    var QRMath = function() {

        var EXP_TABLE = new Array(256);
        var LOG_TABLE = new Array(256);

        // initialize tables
        for (var i = 0; i < 8; i += 1) {
            EXP_TABLE[i] = 1 << i;
        }
        for (var i = 8; i < 256; i += 1) {
            EXP_TABLE[i] = EXP_TABLE[i - 4]
                ^ EXP_TABLE[i - 5]
                ^ EXP_TABLE[i - 6]
                ^ EXP_TABLE[i - 8];
        }
        for (var i = 0; i < 255; i += 1) {
            LOG_TABLE[EXP_TABLE[i] ] = i;
        }

        var _this = {};

        _this.glog = function(n) {

            if (n < 1) {
                throw new Error('glog(' + n + ')');
            }

            return LOG_TABLE[n];
        };

        _this.gexp = function(n) {

            while (n < 0) {
                n += 255;
            }

            while (n >= 256) {
                n -= 255;
            }

            return EXP_TABLE[n];
        };

        return _this;
    }();

    //---------------------------------------------------------------------
    // qrPolynomial
    //---------------------------------------------------------------------

    function qrPolynomial(num, shift) {

        if (typeof num.length == 'undefined') {
            throw new Error(num.length + '/' + shift);
        }

        var _num = function() {
            var offset = 0;
            while (offset < num.length && num[offset] == 0) {
                offset += 1;
            }
            var _num = new Array(num.length - offset + shift);
            for (var i = 0; i < num.length - offset; i += 1) {
                _num[i] = num[i + offset];
            }
            return _num;
        }();

        var _this = {};

        _this.getAt = function(index) {
            return _num[index];
        };

        _this.getLength = function() {
            return _num.length;
        };

        _this.multiply = function(e) {

            var num = new Array(_this.getLength() + e.getLength() - 1);

            for (var i = 0; i < _this.getLength(); i += 1) {
                for (var j = 0; j < e.getLength(); j += 1) {
                    num[i + j] ^= QRMath.gexp(QRMath.glog(_this.getAt(i) ) + QRMath.glog(e.getAt(j) ) );
                }
            }

            return qrPolynomial(num, 0);
        };

        _this.mod = function(e) {

            if (_this.getLength() - e.getLength() < 0) {
                return _this;
            }

            var ratio = QRMath.glog(_this.getAt(0) ) - QRMath.glog(e.getAt(0) );

            var num = new Array(_this.getLength() );
            for (var i = 0; i < _this.getLength(); i += 1) {
                num[i] = _this.getAt(i);
            }

            for (var i = 0; i < e.getLength(); i += 1) {
                num[i] ^= QRMath.gexp(QRMath.glog(e.getAt(i) ) + ratio);
            }

            // recursive call
            return qrPolynomial(num, 0).mod(e);
        };

        return _this;
    };

    //---------------------------------------------------------------------
    // QRRSBlock
    //---------------------------------------------------------------------

    var QRRSBlock = function() {

        var RS_BLOCK_TABLE = [

            // L
            // M
            // Q
            // H

            // 1
            [1, 26, 19],
            [1, 26, 16],
            [1, 26, 13],
            [1, 26, 9],

            // 2
            [1, 44, 34],
            [1, 44, 28],
            [1, 44, 22],
            [1, 44, 16],

            // 3
            [1, 70, 55],
            [1, 70, 44],
            [2, 35, 17],
            [2, 35, 13],

            // 4
            [1, 100, 80],
            [2, 50, 32],
            [2, 50, 24],
            [4, 25, 9],

            // 5
            [1, 134, 108],
            [2, 67, 43],
            [2, 33, 15, 2, 34, 16],
            [2, 33, 11, 2, 34, 12],

            // 6
            [2, 86, 68],
            [4, 43, 27],
            [4, 43, 19],
            [4, 43, 15],

            // 7
            [2, 98, 78],
            [4, 49, 31],
            [2, 32, 14, 4, 33, 15],
            [4, 39, 13, 1, 40, 14],

            // 8
            [2, 121, 97],
            [2, 60, 38, 2, 61, 39],
            [4, 40, 18, 2, 41, 19],
            [4, 40, 14, 2, 41, 15],

            // 9
            [2, 146, 116],
            [3, 58, 36, 2, 59, 37],
            [4, 36, 16, 4, 37, 17],
            [4, 36, 12, 4, 37, 13],

            // 10
            [2, 86, 68, 2, 87, 69],
            [4, 69, 43, 1, 70, 44],
            [6, 43, 19, 2, 44, 20],
            [6, 43, 15, 2, 44, 16]
        ];

        var qrRSBlock = function(totalCount, dataCount) {
            var _this = {};
            _this.totalCount = totalCount;
            _this.dataCount = dataCount;
            return _this;
        };

        var _this = {};

        var getRsBlockTable = function(typeNumber, errorCorrectLevel) {

            switch(errorCorrectLevel) {
            case QRErrorCorrectLevel.L :
                return RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 0];
            case QRErrorCorrectLevel.M :
                return RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 1];
            case QRErrorCorrectLevel.Q :
                return RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 2];
            case QRErrorCorrectLevel.H :
                return RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 3];
            default :
                return undefined;
            }
        };

        _this.getRSBlocks = function(typeNumber, errorCorrectLevel) {

            var rsBlock = getRsBlockTable(typeNumber, errorCorrectLevel);

            if (typeof rsBlock == 'undefined') {
                throw new Error('bad rs block @ typeNumber:' + typeNumber +
                        '/errorCorrectLevel:' + errorCorrectLevel);
            }

            var length = rsBlock.length / 3;

            var list = new Array();

            for (var i = 0; i < length; i += 1) {

                var count = rsBlock[i * 3 + 0];
                var totalCount = rsBlock[i * 3 + 1];
                var dataCount = rsBlock[i * 3 + 2];

                for (var j = 0; j < count; j += 1) {
                    list.push(qrRSBlock(totalCount, dataCount) );
                }
            }

            return list;
        };

        return _this;
    }();

    //---------------------------------------------------------------------
    // qrBitBuffer
    //---------------------------------------------------------------------

    var qrBitBuffer = function() {

        var _buffer = new Array();
        var _length = 0;

        var _this = {};

        _this.getBuffer = function() {
            return _buffer;
        };

        _this.getAt = function(index) {
            var bufIndex = Math.floor(index / 8);
            return ( (_buffer[bufIndex] >>> (7 - index % 8) ) & 1) == 1;
        };

        _this.put = function(num, length) {
            for (var i = 0; i < length; i += 1) {
                _this.putBit( ( (num >>> (length - i - 1) ) & 1) == 1);
            }
        };

        _this.getLengthInBits = function() {
            return _length;
        };

        _this.putBit = function(bit) {

            var bufIndex = Math.floor(_length / 8);
            if (_buffer.length <= bufIndex) {
                _buffer.push(0);
            }

            if (bit) {
                _buffer[bufIndex] |= (0x80 >>> (_length % 8) );
            }

            _length += 1;
        };

        return _this;
    };

    //---------------------------------------------------------------------
    // qr8BitByte
    //---------------------------------------------------------------------

    var qr8BitByte = function(data) {

        var _mode = QRMode.MODE_8BIT_BYTE;
        var _data = data;
        var _bytes = qrcode.stringToBytes(data);

        var _this = {};

        _this.getMode = function() {
            return _mode;
        };

        _this.getLength = function(buffer) {
            return _bytes.length;
        };

        _this.write = function(buffer) {
            for (var i = 0; i < _bytes.length; i += 1) {
                buffer.put(_bytes[i], 8);
            }
        };

        return _this;
    };

    //=====================================================================
    // GIF Support etc.
    //

    //---------------------------------------------------------------------
    // byteArrayOutputStream
    //---------------------------------------------------------------------

    var byteArrayOutputStream = function() {

        var _bytes = new Array();

        var _this = {};

        _this.writeByte = function(b) {
            _bytes.push(b & 0xff);
        };

        _this.writeShort = function(i) {
            _this.writeByte(i);
            _this.writeByte(i >>> 8);
        };

        _this.writeBytes = function(b, off, len) {
            off = off || 0;
            len = len || b.length;
            for (var i = 0; i < len; i += 1) {
                _this.writeByte(b[i + off]);
            }
        };

        _this.writeString = function(s) {
            for (var i = 0; i < s.length; i += 1) {
                _this.writeByte(s.charCodeAt(i) );
            }
        };

        _this.toByteArray = function() {
            return _bytes;
        };

        _this.toString = function() {
            var s = '';
            s += '[';
            for (var i = 0; i < _bytes.length; i += 1) {
                if (i > 0) {
                    s += ',';
                }
                s += _bytes[i];
            }
            s += ']';
            return s;
        };

        return _this;
    };

    //---------------------------------------------------------------------
    // base64EncodeOutputStream
    //---------------------------------------------------------------------

    var base64EncodeOutputStream = function() {

        var _buffer = 0;
        var _buflen = 0;
        var _length = 0;
        var _base64 = '';

        var _this = {};

        var writeEncoded = function(b) {
            _base64 += String.fromCharCode(encode(b & 0x3f) );
        };

        var encode = function(n) {
            if (n < 0) {
                // error.
            } else if (n < 26) {
                return 0x41 + n;
            } else if (n < 52) {
                return 0x61 + (n - 26);
            } else if (n < 62) {
                return 0x30 + (n - 52);
            } else if (n == 62) {
                return 0x2b;
            } else if (n == 63) {
                return 0x2f;
            }
            throw new Error('n:' + n);
        };

        _this.writeByte = function(n) {

            _buffer = (_buffer << 8) | (n & 0xff);
            _buflen += 8;
            _length += 1;

            while (_buflen >= 6) {
                writeEncoded(_buffer >>> (_buflen - 6) );
                _buflen -= 6;
            }
        };

        _this.flush = function() {

            if (_buflen > 0) {
                writeEncoded(_buffer << (6 - _buflen) );
                _buffer = 0;
                _buflen = 0;
            }

            if (_length % 3 != 0) {
                // padding
                var padlen = 3 - _length % 3;
                for (var i = 0; i < padlen; i += 1) {
                    _base64 += '=';
                }
            }
        };

        _this.toString = function() {
            return _base64;
        };

        return _this;
    };

    //---------------------------------------------------------------------
    // base64DecodeInputStream
    //---------------------------------------------------------------------

    var base64DecodeInputStream = function(str) {

        var _str = str;
        var _pos = 0;
        var _buffer = 0;
        var _buflen = 0;

        var _this = {};

        _this.read = function() {

            while (_buflen < 8) {

                if (_pos >= _str.length) {
                    if (_buflen == 0) {
                        return -1;
                    }
                    throw new Error('unexpected end of file./' + _buflen);
                }

                var c = _str.charAt(_pos);
                _pos += 1;

                if (c == '=') {
                    _buflen = 0;
                    return -1;
                } else if (c.match(/^\s$/) ) {
                    // ignore if whitespace.
                    continue;
                }

                _buffer = (_buffer << 6) | decode(c.charCodeAt(0) );
                _buflen += 6;
            }

            var n = (_buffer >>> (_buflen - 8) ) & 0xff;
            _buflen -= 8;
            return n;
        };

        var decode = function(c) {
            if (0x41 <= c && c <= 0x5a) {
                return c - 0x41;
            } else if (0x61 <= c && c <= 0x7a) {
                return c - 0x61 + 26;
            } else if (0x30 <= c && c <= 0x39) {
                return c - 0x30 + 52;
            } else if (c == 0x2b) {
                return 62;
            } else if (c == 0x2f) {
                return 63;
            } else {
                throw new Error('c:' + c);
            }
        };

        return _this;
    };

    //---------------------------------------------------------------------
    // gifImage (B/W)
    //---------------------------------------------------------------------

    var gifImage = function(width, height) {

        var _width = width;
        var _height = height;
        var _data = new Array(width * height);

        var _this = {};

        _this.setPixel = function(x, y, pixel) {
            _data[y * _width + x] = pixel;
        };

        _this.write = function(out) {

            //---------------------------------
            // GIF Signature

            out.writeString('GIF87a');

            //---------------------------------
            // Screen Descriptor

            out.writeShort(_width);
            out.writeShort(_height);

            out.writeByte(0x80); // 2bit
            out.writeByte(0);
            out.writeByte(0);

            //---------------------------------
            // Global Color Map

            // black
            out.writeByte(0x00);
            out.writeByte(0x00);
            out.writeByte(0x00);

            // white
            out.writeByte(0xff);
            out.writeByte(0xff);
            out.writeByte(0xff);

            //---------------------------------
            // Image Descriptor

            out.writeString(',');
            out.writeShort(0);
            out.writeShort(0);
            out.writeShort(_width);
            out.writeShort(_height);
            out.writeByte(0);

            //---------------------------------
            // Local Color Map

            //---------------------------------
            // Raster Data

            var lzwMinCodeSize = 2;
            var raster = getLZWRaster(lzwMinCodeSize);

            out.writeByte(lzwMinCodeSize);

            var offset = 0;

            while (raster.length - offset > 255) {
                out.writeByte(255);
                out.writeBytes(raster, offset, 255);
                offset += 255;
            }

            out.writeByte(raster.length - offset);
            out.writeBytes(raster, offset, raster.length - offset);
            out.writeByte(0x00);

            //---------------------------------
            // GIF Terminator
            out.writeString(';');
        };

        var bitOutputStream = function(out) {

            var _out = out;
            var _bitLength = 0;
            var _bitBuffer = 0;

            var _this = {};

            _this.write = function(data, length) {

                if ( (data >>> length) != 0) {
                    throw new Error('length over');
                }

                while (_bitLength + length >= 8) {
                    _out.writeByte(0xff & ( (data << _bitLength) | _bitBuffer) );
                    length -= (8 - _bitLength);
                    data >>>= (8 - _bitLength);
                    _bitBuffer = 0;
                    _bitLength = 0;
                }

                _bitBuffer = (data << _bitLength) | _bitBuffer;
                _bitLength = _bitLength + length;
            };

            _this.flush = function() {
                if (_bitLength > 0) {
                    _out.writeByte(_bitBuffer);
                }
            };

            return _this;
        };

        var getLZWRaster = function(lzwMinCodeSize) {

            var clearCode = 1 << lzwMinCodeSize;
            var endCode = (1 << lzwMinCodeSize) + 1;
            var bitLength = lzwMinCodeSize + 1;

            // Setup LZWTable
            var table = lzwTable();

            for (var i = 0; i < clearCode; i += 1) {
                table.add(String.fromCharCode(i) );
            }
            table.add(String.fromCharCode(clearCode) );
            table.add(String.fromCharCode(endCode) );

            var byteOut = byteArrayOutputStream();
            var bitOut = bitOutputStream(byteOut);

            // clear code
            bitOut.write(clearCode, bitLength);

            var dataIndex = 0;

            var s = String.fromCharCode(_data[dataIndex]);
            dataIndex += 1;

            while (dataIndex < _data.length) {

                var c = String.fromCharCode(_data[dataIndex]);
                dataIndex += 1;

                if (table.contains(s + c) ) {

                    s = s + c;

                } else {

                    bitOut.write(table.indexOf(s), bitLength);

                    if (table.size() < 0xfff) {

                        if (table.size() == (1 << bitLength) ) {
                            bitLength += 1;
                        }

                        table.add(s + c);
                    }

                    s = c;
                }
            }

            bitOut.write(table.indexOf(s), bitLength);

            // end code
            bitOut.write(endCode, bitLength);

            bitOut.flush();

            return byteOut.toByteArray();
        };

        var lzwTable = function() {

            var _map = {};
            var _size = 0;

            var _this = {};

            _this.add = function(key) {
                if (_this.contains(key) ) {
                    throw new Error('dup key:' + key);
                }
                _map[key] = _size;
                _size += 1;
            };

            _this.size = function() {
                return _size;
            };

            _this.indexOf = function(key) {
                return _map[key];
            };

            _this.contains = function(key) {
                return typeof _map[key] != 'undefined';
            };

            return _this;
        };

        return _this;
    };

    var createImgTag = function(width, height, getPixel, alt) {

        var gif = gifImage(width, height);
        for (var y = 0; y < height; y += 1) {
            for (var x = 0; x < width; x += 1) {
                gif.setPixel(x, y, getPixel(x, y) );
            }
        }

        var b = byteArrayOutputStream();
        gif.write(b);

        var base64 = base64EncodeOutputStream();
        var bytes = b.toByteArray();
        for (var i = 0; i < bytes.length; i += 1) {
            base64.writeByte(bytes[i]);
        }
        base64.flush();

        var img = '';
        img += '<img';
        img += '\u0020src="';
        img += 'data:image/gif;base64,';
        img += base64;
        img += '"';
        img += '\u0020width="';
        img += width;
        img += '"';
        img += '\u0020height="';
        img += height;
        img += '"';
        if (alt) {
            img += '\u0020alt="';
            img += alt;
            img += '"';
        }
        img += '/>';

        return img;
    };

    //---------------------------------------------------------------------
    // returns qrcode function.

    return qrcode;
}();
  </script> 
  <script>
    _aa={};_aa._ab=function(f,e){var d=qrcode.width;var b=qrcode.height;var c=true;for(var g=0;g<e.Length&&c;g+=2){var a=Math.floor(e[g]);var h=Math.floor(e[g+1]);if(a<-1||a>d||h<-1||h>b){throw"Error._ab "}c=false;if(a==-1){e[g]=0;c=true}else{if(a==d){e[g]=d-1;c=true}}if(h==-1){e[g+1]=0;c=true}else{if(h==b){e[g+1]=b-1;c=true}}}c=true;for(var g=e.Length-2;g>=0&&c;g-=2){var a=Math.floor(e[g]);var h=Math.floor(e[g+1]);if(a<-1||a>d||h<-1||h>b){throw"Error._ab "}c=false;if(a==-1){e[g]=0;c=true}else{if(a==d){e[g]=d-1;c=true}}if(h==-1){e[g+1]=0;c=true}else{if(h==b){e[g+1]=b-1;c=true}}}};_aa._af=function(b,d,a){var l=new _ac(d);var k=new Array(d<<1);for(var g=0;g<d;g++){var h=k.length;var j=g+0.5;for(var i=0;i<h;i+=2){k[i]=(i>>1)+0.5;k[i+1]=j}a._ad(k);_aa._ab(b,k);try{for(var i=0;i<h;i+=2){var e=(Math.floor(k[i])*4)+(Math.floor(k[i+1])*qrcode.width*4);var f=b[Math.floor(k[i])+qrcode.width*Math.floor(k[i+1])];qrcode.imagedata.data[e]=f?255:0;qrcode.imagedata.data[e+1]=f?255:0;qrcode.imagedata.data[e+2]=0;qrcode.imagedata.data[e+3]=255;if(f){l._dq(i>>1,g)}}}catch(c){throw"Error._ab"}}return l};_aa._ah=function(h,o,l,k,r,q,b,a,f,e,n,m,t,s,d,c,j,i){var g=_ae._ag(l,k,r,q,b,a,f,e,n,m,t,s,d,c,j,i);return _aa._af(h,o,g)};function _a1(b,a){this.count=b;this._fc=a;this.__defineGetter__("Count",function(){return this.count});this.__defineGetter__("_dm",function(){return this._fc})}function _a2(a,c,b){this._bm=a;if(b){this._do=new Array(c,b)}else{this._do=new Array(c)}this.__defineGetter__("_bo",function(){return this._bm});this.__defineGetter__("_dn",function(){return this._bm*this._fo});this.__defineGetter__("_fo",function(){var e=0;for(var d=0;d<this._do.length;d++){e+=this._do[d].length}return e});this._fb=function(){return this._do}}function _a3(k,l,h,g,f,e){this._bs=k;this._ar=l;this._do=new Array(h,g,f,e);var j=0;var b=h._bo;var a=h._fb();for(var d=0;d<a.length;d++){var c=a[d];j+=c.Count*(c._dm+b)}this._br=j;this.__defineGetter__("_fd",function(){return this._bs});this.__defineGetter__("_as",function(){return this._ar});this.__defineGetter__("_dp",function(){return this._br});this.__defineGetter__("_cr",function(){return 17+4*this._bs});this._aq=function(){var r=this._cr;var o=new _ac(r);o._bq(0,0,9,9);o._bq(r-8,0,8,9);o._bq(0,r-8,9,8);var n=this._ar.length;for(var m=0;m<n;m++){var q=this._ar[m]-2;for(var s=0;s<n;s++){if((m==0&&(s==0||s==n-1))||(m==n-1&&s==0)){continue}o._bq(this._ar[s]-2,q,5,5)}}o._bq(6,9,1,r-17);o._bq(9,6,r-17,1);if(this._bs>6){o._bq(r-11,0,3,6);o._bq(0,r-11,6,3)}return o};this._bu=function(i){return this._do[i.ordinal()]}}_a3._bv=new Array(31892,34236,39577,42195,48118,51042,55367,58893,63784,68472,70749,76311,79154,84390,87683,92361,96236,102084,102881,110507,110734,117786,119615,126325,127568,133589,136944,141498,145311,150283,152622,158308,161089,167017);_a3.VERSIONS=_ay();_a3._av=function(a){if(a<1||a>40){throw"bad arguments"}return _a3.VERSIONS[a-1]};_a3._at=function(b){if(b%4!=1){throw"Error _at"}try{return _a3._av((b-17)>>2)}catch(a){throw"Error _av"}};_a3._aw=function(d){var b=4294967295;var f=0;for(var c=0;c<_a3._bv.length;c++){var a=_a3._bv[c];if(a==d){return this._av(c+7)}var e=_ax._gj(d,a);if(e<b){f=c+7;b=e}}if(b<=3){return this._av(f)}return null};function _ay(){return new Array(new _a3(1,new Array(),new _a2(7,new _a1(1,19)),new _a2(10,new _a1(1,16)),new _a2(13,new _a1(1,13)),new _a2(17,new _a1(1,9))),new _a3(2,new Array(6,18),new _a2(10,new _a1(1,34)),new _a2(16,new _a1(1,28)),new _a2(22,new _a1(1,22)),new _a2(28,new _a1(1,16))),new _a3(3,new Array(6,22),new _a2(15,new _a1(1,55)),new _a2(26,new _a1(1,44)),new _a2(18,new _a1(2,17)),new _a2(22,new _a1(2,13))),new _a3(4,new Array(6,26),new _a2(20,new _a1(1,80)),new _a2(18,new _a1(2,32)),new _a2(26,new _a1(2,24)),new _a2(16,new _a1(4,9))),new _a3(5,new Array(6,30),new _a2(26,new _a1(1,108)),new _a2(24,new _a1(2,43)),new _a2(18,new _a1(2,15),new _a1(2,16)),new _a2(22,new _a1(2,11),new _a1(2,12))),new _a3(6,new Array(6,34),new _a2(18,new _a1(2,68)),new _a2(16,new _a1(4,27)),new _a2(24,new _a1(4,19)),new _a2(28,new _a1(4,15))),new _a3(7,new Array(6,22,38),new _a2(20,new _a1(2,78)),new _a2(18,new _a1(4,31)),new _a2(18,new _a1(2,14),new _a1(4,15)),new _a2(26,new _a1(4,13),new _a1(1,14))),new _a3(8,new Array(6,24,42),new _a2(24,new _a1(2,97)),new _a2(22,new _a1(2,38),new _a1(2,39)),new _a2(22,new _a1(4,18),new _a1(2,19)),new _a2(26,new _a1(4,14),new _a1(2,15))),new _a3(9,new Array(6,26,46),new _a2(30,new _a1(2,116)),new _a2(22,new _a1(3,36),new _a1(2,37)),new _a2(20,new _a1(4,16),new _a1(4,17)),new _a2(24,new _a1(4,12),new _a1(4,13))),new _a3(10,new Array(6,28,50),new _a2(18,new _a1(2,68),new _a1(2,69)),new _a2(26,new _a1(4,43),new _a1(1,44)),new _a2(24,new _a1(6,19),new _a1(2,20)),new _a2(28,new _a1(6,15),new _a1(2,16))),new _a3(11,new Array(6,30,54),new _a2(20,new _a1(4,81)),new _a2(30,new _a1(1,50),new _a1(4,51)),new _a2(28,new _a1(4,22),new _a1(4,23)),new _a2(24,new _a1(3,12),new _a1(8,13))),new _a3(12,new Array(6,32,58),new _a2(24,new _a1(2,92),new _a1(2,93)),new _a2(22,new _a1(6,36),new _a1(2,37)),new _a2(26,new _a1(4,20),new _a1(6,21)),new _a2(28,new _a1(7,14),new _a1(4,15))),new _a3(13,new Array(6,34,62),new _a2(26,new _a1(4,107)),new _a2(22,new _a1(8,37),new _a1(1,38)),new _a2(24,new _a1(8,20),new _a1(4,21)),new _a2(22,new _a1(12,11),new _a1(4,12))),new _a3(14,new Array(6,26,46,66),new _a2(30,new _a1(3,115),new _a1(1,116)),new _a2(24,new _a1(4,40),new _a1(5,41)),new _a2(20,new _a1(11,16),new _a1(5,17)),new _a2(24,new _a1(11,12),new _a1(5,13))),new _a3(15,new Array(6,26,48,70),new _a2(22,new _a1(5,87),new _a1(1,88)),new _a2(24,new _a1(5,41),new _a1(5,42)),new _a2(30,new _a1(5,24),new _a1(7,25)),new _a2(24,new _a1(11,12),new _a1(7,13))),new _a3(16,new Array(6,26,50,74),new _a2(24,new _a1(5,98),new _a1(1,99)),new _a2(28,new _a1(7,45),new _a1(3,46)),new _a2(24,new _a1(15,19),new _a1(2,20)),new _a2(30,new _a1(3,15),new _a1(13,16))),new _a3(17,new Array(6,30,54,78),new _a2(28,new _a1(1,107),new _a1(5,108)),new _a2(28,new _a1(10,46),new _a1(1,47)),new _a2(28,new _a1(1,22),new _a1(15,23)),new _a2(28,new _a1(2,14),new _a1(17,15))),new _a3(18,new Array(6,30,56,82),new _a2(30,new _a1(5,120),new _a1(1,121)),new _a2(26,new _a1(9,43),new _a1(4,44)),new _a2(28,new _a1(17,22),new _a1(1,23)),new _a2(28,new _a1(2,14),new _a1(19,15))),new _a3(19,new Array(6,30,58,86),new _a2(28,new _a1(3,113),new _a1(4,114)),new _a2(26,new _a1(3,44),new _a1(11,45)),new _a2(26,new _a1(17,21),new _a1(4,22)),new _a2(26,new _a1(9,13),new _a1(16,14))),new _a3(20,new Array(6,34,62,90),new _a2(28,new _a1(3,107),new _a1(5,108)),new _a2(26,new _a1(3,41),new _a1(13,42)),new _a2(30,new _a1(15,24),new _a1(5,25)),new _a2(28,new _a1(15,15),new _a1(10,16))),new _a3(21,new Array(6,28,50,72,94),new _a2(28,new _a1(4,116),new _a1(4,117)),new _a2(26,new _a1(17,42)),new _a2(28,new _a1(17,22),new _a1(6,23)),new _a2(30,new _a1(19,16),new _a1(6,17))),new _a3(22,new Array(6,26,50,74,98),new _a2(28,new _a1(2,111),new _a1(7,112)),new _a2(28,new _a1(17,46)),new _a2(30,new _a1(7,24),new _a1(16,25)),new _a2(24,new _a1(34,13))),new _a3(23,new Array(6,30,54,74,102),new _a2(30,new _a1(4,121),new _a1(5,122)),new _a2(28,new _a1(4,47),new _a1(14,48)),new _a2(30,new _a1(11,24),new _a1(14,25)),new _a2(30,new _a1(16,15),new _a1(14,16))),new _a3(24,new Array(6,28,54,80,106),new _a2(30,new _a1(6,117),new _a1(4,118)),new _a2(28,new _a1(6,45),new _a1(14,46)),new _a2(30,new _a1(11,24),new _a1(16,25)),new _a2(30,new _a1(30,16),new _a1(2,17))),new _a3(25,new Array(6,32,58,84,110),new _a2(26,new _a1(8,106),new _a1(4,107)),new _a2(28,new _a1(8,47),new _a1(13,48)),new _a2(30,new _a1(7,24),new _a1(22,25)),new _a2(30,new _a1(22,15),new _a1(13,16))),new _a3(26,new Array(6,30,58,86,114),new _a2(28,new _a1(10,114),new _a1(2,115)),new _a2(28,new _a1(19,46),new _a1(4,47)),new _a2(28,new _a1(28,22),new _a1(6,23)),new _a2(30,new _a1(33,16),new _a1(4,17))),new _a3(27,new Array(6,34,62,90,118),new _a2(30,new _a1(8,122),new _a1(4,123)),new _a2(28,new _a1(22,45),new _a1(3,46)),new _a2(30,new _a1(8,23),new _a1(26,24)),new _a2(30,new _a1(12,15),new _a1(28,16))),new _a3(28,new Array(6,26,50,74,98,122),new _a2(30,new _a1(3,117),new _a1(10,118)),new _a2(28,new _a1(3,45),new _a1(23,46)),new _a2(30,new _a1(4,24),new _a1(31,25)),new _a2(30,new _a1(11,15),new _a1(31,16))),new _a3(29,new Array(6,30,54,78,102,126),new _a2(30,new _a1(7,116),new _a1(7,117)),new _a2(28,new _a1(21,45),new _a1(7,46)),new _a2(30,new _a1(1,23),new _a1(37,24)),new _a2(30,new _a1(19,15),new _a1(26,16))),new _a3(30,new Array(6,26,52,78,104,130),new _a2(30,new _a1(5,115),new _a1(10,116)),new _a2(28,new _a1(19,47),new _a1(10,48)),new _a2(30,new _a1(15,24),new _a1(25,25)),new _a2(30,new _a1(23,15),new _a1(25,16))),new _a3(31,new Array(6,30,56,82,108,134),new _a2(30,new _a1(13,115),new _a1(3,116)),new _a2(28,new _a1(2,46),new _a1(29,47)),new _a2(30,new _a1(42,24),new _a1(1,25)),new _a2(30,new _a1(23,15),new _a1(28,16))),new _a3(32,new Array(6,34,60,86,112,138),new _a2(30,new _a1(17,115)),new _a2(28,new _a1(10,46),new _a1(23,47)),new _a2(30,new _a1(10,24),new _a1(35,25)),new _a2(30,new _a1(19,15),new _a1(35,16))),new _a3(33,new Array(6,30,58,86,114,142),new _a2(30,new _a1(17,115),new _a1(1,116)),new _a2(28,new _a1(14,46),new _a1(21,47)),new _a2(30,new _a1(29,24),new _a1(19,25)),new _a2(30,new _a1(11,15),new _a1(46,16))),new _a3(34,new Array(6,34,62,90,118,146),new _a2(30,new _a1(13,115),new _a1(6,116)),new _a2(28,new _a1(14,46),new _a1(23,47)),new _a2(30,new _a1(44,24),new _a1(7,25)),new _a2(30,new _a1(59,16),new _a1(1,17))),new _a3(35,new Array(6,30,54,78,102,126,150),new _a2(30,new _a1(12,121),new _a1(7,122)),new _a2(28,new _a1(12,47),new _a1(26,48)),new _a2(30,new _a1(39,24),new _a1(14,25)),new _a2(30,new _a1(22,15),new _a1(41,16))),new _a3(36,new Array(6,24,50,76,102,128,154),new _a2(30,new _a1(6,121),new _a1(14,122)),new _a2(28,new _a1(6,47),new _a1(34,48)),new _a2(30,new _a1(46,24),new _a1(10,25)),new _a2(30,new _a1(2,15),new _a1(64,16))),new _a3(37,new Array(6,28,54,80,106,132,158),new _a2(30,new _a1(17,122),new _a1(4,123)),new _a2(28,new _a1(29,46),new _a1(14,47)),new _a2(30,new _a1(49,24),new _a1(10,25)),new _a2(30,new _a1(24,15),new _a1(46,16))),new _a3(38,new Array(6,32,58,84,110,136,162),new _a2(30,new _a1(4,122),new _a1(18,123)),new _a2(28,new _a1(13,46),new _a1(32,47)),new _a2(30,new _a1(48,24),new _a1(14,25)),new _a2(30,new _a1(42,15),new _a1(32,16))),new _a3(39,new Array(6,26,54,82,110,138,166),new _a2(30,new _a1(20,117),new _a1(4,118)),new _a2(28,new _a1(40,47),new _a1(7,48)),new _a2(30,new _a1(43,24),new _a1(22,25)),new _a2(30,new _a1(10,15),new _a1(67,16))),new _a3(40,new Array(6,30,58,86,114,142,170),new _a2(30,new _a1(19,118),new _a1(6,119)),new _a2(28,new _a1(18,47),new _a1(31,48)),new _a2(30,new _a1(34,24),new _a1(34,25)),new _a2(30,new _a1(20,15),new _a1(61,16))))}function _ae(i,f,c,h,e,b,g,d,a){this.a11=i;this.a12=h;this.a13=g;this.a21=f;this.a22=e;this.a23=d;this.a31=c;this.a32=b;this.a33=a;this._ad=function(w){var t=w.length;var A=this.a11;var z=this.a12;var v=this.a13;var r=this.a21;var q=this.a22;var o=this.a23;var m=this.a31;var k=this.a32;var j=this.a33;for(var n=0;n<t;n+=2){var u=w[n];var s=w[n+1];var l=v*u+o*s+j;w[n]=(A*u+r*s+m)/l;w[n+1]=(z*u+q*s+k)/l}};this._fp=function(m,k){var r=m.length;for(var l=0;l<r;l++){var j=m[l];var q=k[l];var o=this.a13*j+this.a23*q+this.a33;m[l]=(this.a11*j+this.a21*q+this.a31)/o;k[l]=(this.a12*j+this.a22*q+this.a32)/o}};this._fr=function(){return new _ae(this.a22*this.a33-this.a23*this.a32,this.a23*this.a31-this.a21*this.a33,this.a21*this.a32-this.a22*this.a31,this.a13*this.a32-this.a12*this.a33,this.a11*this.a33-this.a13*this.a31,this.a12*this.a31-this.a11*this.a32,this.a12*this.a23-this.a13*this.a22,this.a13*this.a21-this.a11*this.a23,this.a11*this.a22-this.a12*this.a21)};this.times=function(j){return new _ae(this.a11*j.a11+this.a21*j.a12+this.a31*j.a13,this.a11*j.a21+this.a21*j.a22+this.a31*j.a23,this.a11*j.a31+this.a21*j.a32+this.a31*j.a33,this.a12*j.a11+this.a22*j.a12+this.a32*j.a13,this.a12*j.a21+this.a22*j.a22+this.a32*j.a23,this.a12*j.a31+this.a22*j.a32+this.a32*j.a33,this.a13*j.a11+this.a23*j.a12+this.a33*j.a13,this.a13*j.a21+this.a23*j.a22+this.a33*j.a23,this.a13*j.a31+this.a23*j.a32+this.a33*j.a33)}}_ae._ag=function(q,e,o,d,n,c,m,b,h,r,l,f,a,j,i,s){var g=this._be(q,e,o,d,n,c,m,b);var k=this._bf(h,r,l,f,a,j,i,s);return k.times(g)};_ae._bf=function(f,h,d,g,b,e,a,c){dy2=c-e;dy3=h-g+e-c;if(dy2==0&&dy3==0){return new _ae(d-f,b-d,f,g-h,e-g,h,0,0,1)}else{dx1=d-b;dx2=a-b;dx3=f-d+b-a;dy1=g-e;_dr=dx1*dy2-dx2*dy1;a13=(dx3*dy2-dx2*dy3)/_dr;a23=(dx1*dy3-dx3*dy1)/_dr;return new _ae(d-f+a13*d,a-f+a23*a,f,g-h+a13*g,c-h+a23*c,h,a13,a23,1)}};_ae._be=function(f,h,d,g,b,e,a,c){return this._bf(f,h,d,g,b,e,a,c)._fr()};function _bg(b,a){this.bits=b;this.points=a}function Detector(a){this.image=a;this._am=null;this._bi=function(m,l,c,b){var d=Math.abs(b-l)>Math.abs(c-m);if(d){var s=m;m=l;l=s;s=c;c=b;b=s}var j=Math.abs(c-m);var i=Math.abs(b-l);var q=-j>>1;var v=l<b?1:-1;var f=m<c?1:-1;var e=0;for(var h=m,g=l;h!=c;h+=f){var u=d?g:h;var t=d?h:g;if(e==1){if(this.image[u+t*qrcode.width]){e++}}else{if(!this.image[u+t*qrcode.width]){e++}}if(e==3){var o=h-m;var n=g-l;return Math.sqrt((o*o+n*n))}q+=i;if(q>0){if(g==b){break}g+=v;q-=j}}var k=c-m;var r=b-l;return Math.sqrt((k*k+r*r))};this._bh=function(i,g,h,f){var b=this._bi(i,g,h,f);var e=1;var d=i-(h-i);if(d<0){e=i/(i-d);d=0}else{if(d>=qrcode.width){e=(qrcode.width-1-i)/(d-i);d=qrcode.width-1}}var c=Math.floor(g-(f-g)*e);e=1;if(c<0){e=g/(g-c);c=0}else{if(c>=qrcode.height){e=(qrcode.height-1-g)/(c-g);c=qrcode.height-1}}d=Math.floor(i+(d-i)*e);b+=this._bi(i,g,d,c);return b-1};this._bj=function(c,d){var b=this._bh(Math.floor(c.X),Math.floor(c.Y),Math.floor(d.X),Math.floor(d.Y));var e=this._bh(Math.floor(d.X),Math.floor(d.Y),Math.floor(c.X),Math.floor(c.Y));if(isNaN(b)){return e/7}if(isNaN(e)){return b/7}return(b+e)/14};this._bk=function(d,c,b){return(this._bj(d,c)+this._bj(d,b))/2};this.distance=function(c,b){xDiff=c.X-b.X;yDiff=c.Y-b.Y;return Math.sqrt((xDiff*xDiff+yDiff*yDiff))};this._bx=function(g,f,d,e){var b=Math.round(this.distance(g,f)/e);var c=Math.round(this.distance(g,d)/e);var h=((b+c)>>1)+7;switch(h&3){case 0:h++;break;case 2:h--;break;case 3:throw"Error"}return h};this._bl=function(g,f,d,j){var k=Math.floor(j*g);var h=Math.max(0,f-k);var i=Math.min(qrcode.width-1,f+k);if(i-h<g*3){throw"Error"}var b=Math.max(0,d-k);var c=Math.min(qrcode.height-1,d+k);var e=new _ak(this.image,h,b,i-h,c-b,g,this._am);return e.find()};this.createTransform=function(l,h,k,b,g){var j=g-3.5;var i;var f;var e;var c;if(b!=null){i=b.X;f=b.Y;e=c=j-3}else{i=(h.X-l.X)+k.X;f=(h.Y-l.Y)+k.Y;e=c=j}var d=_ae._ag(3.5,3.5,j,3.5,e,c,3.5,j,l.X,l.Y,h.X,h.Y,i,f,k.X,k.Y);return d};this._bz=function(e,b,d){var c=_aa;return c._af(e,d,b)};this._cd=function(r){var j=r._gq;var h=r._gs;var n=r._gp;var d=this._bk(j,h,n);if(d<1){throw"Error"}var s=this._bx(j,h,n,d);var b=_a3._at(s);var k=b._cr-7;var l=null;if(b._as.length>0){var f=h.X-j.X+n.X;var e=h.Y-j.Y+n.Y;var c=1-3/k;var u=Math.floor(j.X+c*(f-j.X));var t=Math.floor(j.Y+c*(e-j.Y));for(var q=4;q<=16;q<<=1){l=this._bl(d,u,t,q);break}}var g=this.createTransform(j,h,n,l,s);var m=this._bz(this.image,g,s);var o;if(l==null){o=new Array(n,j,h)}else{o=new Array(n,j,h,l)}return new _bg(m,o)};this.detect=function(){var b=new _cc()._ce(this.image);return this._cd(b)}}var _ca=21522;var _cb=new Array(new Array(21522,0),new Array(20773,1),new Array(24188,2),new Array(23371,3),new Array(17913,4),new Array(16590,5),new Array(20375,6),new Array(19104,7),new Array(30660,8),new Array(29427,9),new Array(32170,10),new Array(30877,11),new Array(26159,12),new Array(25368,13),new Array(27713,14),new Array(26998,15),new Array(5769,16),new Array(5054,17),new Array(7399,18),new Array(6608,19),new Array(1890,20),new Array(597,21),new Array(3340,22),new Array(2107,23),new Array(13663,24),new Array(12392,25),new Array(16177,26),new Array(14854,27),new Array(9396,28),new Array(8579,29),new Array(11994,30),new Array(11245,31));var _ch=new Array(0,1,1,2,1,2,2,3,1,2,2,3,2,3,3,4);function _ax(a){this._cf=_cg.forBits((a>>3)&3);this._fe=(a&7);this.__defineGetter__("_cg",function(){return this._cf});this.__defineGetter__("_dx",function(){return this._fe});this.GetHashCode=function(){return(this._cf.ordinal()<<3)|_fe};this.Equals=function(c){var b=c;return this._cf==b._cf&&this._fe==b._fe}}_ax._gj=function(d,c){d^=c;return _ch[d&15]+_ch[(_ew(d,4)&15)]+_ch[(_ew(d,8)&15)]+_ch[(_ew(d,12)&15)]+_ch[(_ew(d,16)&15)]+_ch[(_ew(d,20)&15)]+_ch[(_ew(d,24)&15)]+_ch[(_ew(d,28)&15)]};_ax._ci=function(a){var b=_ax._cj(a);if(b!=null){return b}return _ax._cj(a^_ca)};_ax._cj=function(d){var b=4294967295;var a=0;for(var c=0;c<_cb.length;c++){var g=_cb[c];var f=g[0];if(f==d){return new _ax(g[1])}var e=this._gj(d,f);if(e<b){a=g[1];b=e}}if(b<=3){return new _ax(a)}return null};function _cg(a,c,b){this._ff=a;this.bits=c;this.name=b;this.__defineGetter__("Bits",function(){return this.bits});this.__defineGetter__("Name",function(){return this.name});this.ordinal=function(){return this._ff}}_cg.forBits=function(a){if(a<0||a>=FOR_BITS.Length){throw"bad arguments"}return FOR_BITS[a]};var L=new _cg(0,1,"L");var M=new _cg(1,0,"M");var Q=new _cg(2,3,"Q");var H=new _cg(3,2,"H");var FOR_BITS=new Array(M,L,H,Q);function _ac(d,a){if(!a){a=d}if(d<1||a<1){throw"Both dimensions must be greater than 0"}this.width=d;this.height=a;var c=d>>5;if((d&31)!=0){c++}this.rowSize=c;this.bits=new Array(c*a);for(var b=0;b<this.bits.length;b++){this.bits[b]=0}this.__defineGetter__("Width",function(){return this.width});this.__defineGetter__("Height",function(){return this.height});this.__defineGetter__("Dimension",function(){if(this.width!=this.height){throw"Can't call getDimension() on a non-square matrix"}return this.width});this._ds=function(e,g){var f=g*this.rowSize+(e>>5);return((_ew(this.bits[f],(e&31)))&1)!=0};this._dq=function(e,g){var f=g*this.rowSize+(e>>5);this.bits[f]|=1<<(e&31)};this.flip=function(e,g){var f=g*this.rowSize+(e>>5);this.bits[f]^=1<<(e&31)};this.clear=function(){var e=this.bits.length;for(var f=0;f<e;f++){this.bits[f]=0}};this._bq=function(g,j,f,m){if(j<0||g<0){throw"Left and top must be nonnegative"}if(m<1||f<1){throw"Height and width must be at least 1"}var l=g+f;var e=j+m;if(e>this.height||l>this.width){throw"The region must fit inside the matrix"}for(var i=j;i<e;i++){var h=i*this.rowSize;for(var k=g;k<l;k++){this.bits[h+(k>>5)]|=1<<(k&31)}}}}function _dl(a,b){this._dv=a;this._dw=b;this.__defineGetter__("_du",function(){return this._dv});this.__defineGetter__("Codewords",function(){return this._dw})}_dl._gn=function(c,h,s){if(c.length!=h._dp){throw"bad arguments"}var k=h._bu(s);var e=0;var d=k._fb();for(var r=0;r<d.length;r++){e+=d[r].Count}var l=new Array(e);var n=0;for(var o=0;o<d.length;o++){var f=d[o];for(var r=0;r<f.Count;r++){var m=f._dm;var t=k._bo+m;l[n++]=new _dl(m,new Array(t))}}var u=l[0]._dw.length;var b=l.length-1;while(b>=0){var w=l[b]._dw.length;if(w==u){break}b--}b++;var g=u-k._bo;var a=0;for(var r=0;r<g;r++){for(var o=0;o<n;o++){l[o]._dw[r]=c[a++]}}for(var o=b;o<n;o++){l[o]._dw[g]=c[a++]}var q=l[0]._dw.length;for(var r=g;r<q;r++){for(var o=0;o<n;o++){var v=o<b?r:r+1;l[o]._dw[v]=c[a++]}}return l};function _cl(a){var b=a.Dimension;if(b<21||(b&3)!=1){throw"Error _cl"}this._au=a;this._cp=null;this._co=null;this._dk=function(d,c,e){return this._au._ds(d,c)?(e<<1)|1:e<<1};this._cm=function(){if(this._co!=null){return this._co}var g=0;for(var e=0;e<6;e++){g=this._dk(e,8,g)}g=this._dk(7,8,g);g=this._dk(8,8,g);g=this._dk(8,7,g);for(var c=5;c>=0;c--){g=this._dk(8,c,g)}this._co=_ax._ci(g);if(this._co!=null){return this._co}var f=this._au.Dimension;g=0;var d=f-8;for(var e=f-1;e>=d;e--){g=this._dk(e,8,g)}for(var c=f-7;c<f;c++){g=this._dk(8,c,g)}this._co=_ax._ci(g);if(this._co!=null){return this._co}throw"Error _cm"};this._cq=function(){if(this._cp!=null){return this._cp}var h=this._au.Dimension;var f=(h-17)>>2;if(f<=6){return _a3._av(f)}var g=0;var e=h-11;for(var c=5;c>=0;c--){for(var d=h-9;d>=e;d--){g=this._dk(d,c,g)}}this._cp=_a3._aw(g);if(this._cp!=null&&this._cp._cr==h){return this._cp}g=0;for(var d=5;d>=0;d--){for(var c=h-9;c>=e;c--){g=this._dk(d,c,g)}}this._cp=_a3._aw(g);if(this._cp!=null&&this._cp._cr==h){return this._cp}throw"Error _cq"};this._gk=function(){var r=this._cm();var o=this._cq();var c=_dx._gl(r._dx);var f=this._au.Dimension;c._dj(this._au,f);var k=o._aq();var n=true;var s=new Array(o._dp);var m=0;var q=0;var h=0;for(var e=f-1;e>0;e-=2){if(e==6){e--}for(var l=0;l<f;l++){var g=n?f-1-l:l;for(var d=0;d<2;d++){if(!k._ds(e-d,g)){h++;q<<=1;if(this._au._ds(e-d,g)){q|=1}if(h==8){s[m++]=q;h=0;q=0}}}}n^=true}if(m!=o._dp){throw"Error _gk"}return s}}_dx={};_dx._gl=function(a){if(a<0||a>7){throw"bad arguments"}return _dx._dy[a]};function _fg(){this._dj=function(c,d){for(var b=0;b<d;b++){for(var a=0;a<d;a++){if(this._fw(b,a)){c.flip(a,b)}}}};this._fw=function(b,a){return((b+a)&1)==0}}function _fh(){this._dj=function(c,d){for(var b=0;b<d;b++){for(var a=0;a<d;a++){if(this._fw(b,a)){c.flip(a,b)}}}};this._fw=function(b,a){return(b&1)==0}}function _fi(){this._dj=function(c,d){for(var b=0;b<d;b++){for(var a=0;a<d;a++){if(this._fw(b,a)){c.flip(a,b)}}}};this._fw=function(b,a){return a%3==0}}function _fj(){this._dj=function(c,d){for(var b=0;b<d;b++){for(var a=0;a<d;a++){if(this._fw(b,a)){c.flip(a,b)}}}};this._fw=function(b,a){return(b+a)%3==0}}function _fk(){this._dj=function(c,d){for(var b=0;b<d;b++){for(var a=0;a<d;a++){if(this._fw(b,a)){c.flip(a,b)}}}};this._fw=function(b,a){return(((_ew(b,1))+(a/3))&1)==0}}function _fl(){this._dj=function(c,d){for(var b=0;b<d;b++){for(var a=0;a<d;a++){if(this._fw(b,a)){c.flip(a,b)}}}};this._fw=function(c,b){var a=c*b;return(a&1)+(a%3)==0}}function _fm(){this._dj=function(c,d){for(var b=0;b<d;b++){for(var a=0;a<d;a++){if(this._fw(b,a)){c.flip(a,b)}}}};this._fw=function(c,b){var a=c*b;return(((a&1)+(a%3))&1)==0}}function _fn(){this._dj=function(c,d){for(var b=0;b<d;b++){for(var a=0;a<d;a++){if(this._fw(b,a)){c.flip(a,b)}}}};this._fw=function(b,a){return((((b+a)&1)+((b*a)%3))&1)==0}}_dx._dy=new Array(new _fg(),new _fh(),new _fi(),new _fj(),new _fk(),new _fl(),new _fm(),new _fn());function _db(_fa){this._fa=_fa;this.decode=function(received,_fv){var poly=new _bp(this._fa,received);var _dh=new Array(_fv);for(var i=0;i<_dh.length;i++){_dh[i]=0}var _fq=false;var noError=true;for(var i=0;i<_fv;i++){var eval=poly.evaluateAt(this._fa.exp(_fq?i+1:i));_dh[_dh.length-1-i]=eval;if(eval!=0){noError=false}}if(noError){return}var _fu=new _bp(this._fa,_dh);var _dg=this._eb(this._fa._ba(_fv,1),_fu,_fv);var sigma=_dg[0];var omega=_dg[1];var _dz=this._ey(sigma);var _ea=this._di(omega,_dz,_fq);for(var i=0;i<_dz.length;i++){var position=received.length-1-this._fa.log(_dz[i]);if(position<0){throw"ReedSolomonException Bad error location"}received[position]=_az._bd(received[position],_ea[i])}};this._eb=function(a,b,R){if(a._ec<b._ec){var temp=a;a=b;b=temp}var rLast=a;var r=b;var sLast=this._fa.One;var s=this._fa.Zero;var tLast=this._fa.Zero;var t=this._fa.One;while(r._ec>=Math.floor(R/2)){var rLastLast=rLast;var _ga=sLast;var _gb=tLast;rLast=r;sLast=s;tLast=t;if(rLast.Zero){throw"r_{i-1} was zero"}r=rLastLast;var q=this._fa.Zero;var _df=rLast._ex(rLast._ec);var _fy=this._fa.inverse(_df);while(r._ec>=rLast._ec&&!r.Zero){var _fx=r._ec-rLast._ec;var scale=this._fa.multiply(r._ex(r._ec),_fy);q=q._bd(this._fa._ba(_fx,scale));r=r._bd(rLast._dc(_fx,scale))}s=q.multiply1(sLast)._bd(_ga);t=q.multiply1(tLast)._bd(_gb)}var _de=t._ex(0);if(_de==0){throw"ReedSolomonException sigmaTilde(0) was zero"}var inverse=this._fa.inverse(_de);var sigma=t.multiply2(inverse);var omega=r.multiply2(inverse);return new Array(sigma,omega)};this._ey=function(_ez){var _fz=_ez._ec;if(_fz==1){return new Array(_ez._ex(1))}var result=new Array(_fz);var e=0;for(var i=1;i<256&&e<_fz;i++){if(_ez.evaluateAt(i)==0){result[e]=this._fa.inverse(i);e++}}if(e!=_fz){throw"Error locator degree does not match number of roots"}return result};this._di=function(_fs,_dz,_fq){var s=_dz.length;var result=new Array(s);for(var i=0;i<s;i++){var _gc=this._fa.inverse(_dz[i]);var _dr=1;for(var j=0;j<s;j++){if(i!=j){_dr=this._fa.multiply(_dr,_az._bd(1,this._fa.multiply(_dz[j],_gc)))}}result[i]=this._fa.multiply(_fs.evaluateAt(_gc),this._fa.inverse(_dr));if(_fq){result[i]=this._fa.multiply(result[i],_gc)}}return result}}function _bp(f,e){if(e==null||e.length==0){throw"bad arguments"}this._fa=f;var c=e.length;if(c>1&&e[0]==0){var d=1;while(d<c&&e[d]==0){d++}if(d==c){this._dd=f.Zero._dd}else{this._dd=new Array(c-d);for(var b=0;b<this._dd.length;b++){this._dd[b]=0}for(var a=0;a<this._dd.length;a++){this._dd[a]=e[d+a]}}}else{this._dd=e}this.__defineGetter__("Zero",function(){return this._dd[0]==0});this.__defineGetter__("_ec",function(){return this._dd.length-1});this.__defineGetter__("Coefficients",function(){return this._dd});this._ex=function(g){return this._dd[this._dd.length-1-g]};this.evaluateAt=function(h){if(h==0){return this._ex(0)}var l=this._dd.length;if(h==1){var g=0;for(var k=0;k<l;k++){g=_az._bd(g,this._dd[k])}return g}var j=this._dd[0];for(var k=1;k<l;k++){j=_az._bd(this._fa.multiply(h,j),this._dd[k])}return j};this._bd=function(g){if(this._fa!=g._fa){throw"GF256Polys do not have same _az _fa"}if(this.Zero){return g}if(g.Zero){return this}var o=this._dd;var n=g._dd;if(o.length>n.length){var j=o;o=n;n=j}var h=new Array(n.length);var k=n.length-o.length;for(var m=0;m<k;m++){h[m]=n[m]}for(var l=k;l<n.length;l++){h[l]=_az._bd(o[l-k],n[l])}return new _bp(f,h)};this.multiply1=function(o){if(this._fa!=o._fa){throw"GF256Polys do not have same _az _fa"}if(this.Zero||o.Zero){return this._fa.Zero}var r=this._dd;var g=r.length;var l=o._dd;var n=l.length;var q=new Array(g+n-1);for(var m=0;m<g;m++){var h=r[m];for(var k=0;k<n;k++){q[m+k]=_az._bd(q[m+k],this._fa.multiply(h,l[k]))}}return new _bp(this._fa,q)};this.multiply2=function(g){if(g==0){return this._fa.Zero}if(g==1){return this}var j=this._dd.length;var k=new Array(j);for(var h=0;h<j;h++){k[h]=this._fa.multiply(this._dd[h],g)}return new _bp(this._fa,k)};this._dc=function(l,g){if(l<0){throw"bad arguments"}if(g==0){return this._fa.Zero}var j=this._dd.length;var k=new Array(j+l);for(var h=0;h<k.length;h++){k[h]=0}for(var h=0;h<j;h++){k[h]=this._fa.multiply(this._dd[h],g)}return new _bp(this._fa,k)};this.divide=function(l){if(this._fa!=l._fa){throw"GF256Polys do not have same _az _fa"}if(l.Zero){throw"Divide by 0"}var j=this._fa.Zero;var o=this;var g=l._ex(l._ec);var n=this._fa.inverse(g);while(o._ec>=l._ec&&!o.Zero){var m=o._ec-l._ec;var h=this._fa.multiply(o._ex(o._ec),n);var i=l._dc(m,h);var k=this._fa._ba(m,h);j=j._bd(k);o=o._bd(i)}return new Array(j,o)}}function _az(b){this._gh=new Array(256);this._gi=new Array(256);var a=1;for(var e=0;e<256;e++){this._gh[e]=a;a<<=1;if(a>=256){a^=b}}for(var e=0;e<255;e++){this._gi[this._gh[e]]=e}var d=new Array(1);d[0]=0;this.zero=new _bp(this,new Array(d));var c=new Array(1);c[0]=1;this.one=new _bp(this,new Array(c));this.__defineGetter__("Zero",function(){return this.zero});this.__defineGetter__("One",function(){return this.one});this._ba=function(j,f){if(j<0){throw"bad arguments"}if(f==0){return zero}var h=new Array(j+1);for(var g=0;g<h.length;g++){h[g]=0}h[0]=f;return new _bp(this,h)};this.exp=function(f){return this._gh[f]};this.log=function(f){if(f==0){throw"bad arguments"}return this._gi[f]};this.inverse=function(f){if(f==0){throw"System.ArithmeticException"}return this._gh[255-this._gi[f]]};this.multiply=function(g,f){if(g==0||f==0){return 0}if(g==1){return f}if(f==1){return g}return this._gh[(this._gi[g]+this._gi[f])%255]}}_az._bb=new _az(285);_az._bc=new _az(301);_az._bd=function(d,c){return d^c};Decoder={};Decoder.rsDecoder=new _db(_az._bb);Decoder.correctErrors=function(g,b){var d=g.length;var f=new Array(d);for(var e=0;e<d;e++){f[e]=g[e]&255}var a=g.length-b;try{Decoder.rsDecoder.decode(f,a)}catch(c){throw c}for(var e=0;e<b;e++){g[e]=f[e]}};Decoder.decode=function(r){var b=new _cl(r);var o=b._cq();var c=b._cm()._cg;var q=b._gk();var a=_dl._gn(q,o,c);var f=0;for(var k=0;k<a.Length;k++){f+=a[k]._du}var e=new Array(f);var n=0;for(var h=0;h<a.length;h++){var m=a[h];var d=m.Codewords;var g=m._du;Decoder.correctErrors(d,g);for(var k=0;k<g;k++){e[n++]=d[k]}}var l=new QRCodeDataBlockReader(e,o._fd,c.Bits);return l};qrcode={};qrcode.imagedata=null;qrcode.width=0;qrcode.height=0;qrcode.qrCodeSymbol=null;qrcode.debug=false;qrcode._eo=[[10,9,8,8],[12,11,16,10],[14,13,16,12]];qrcode.callback=null;qrcode.decode=function(d){if(arguments.length==0){var b=document.getElementById("qr-canvas");var a=b.getContext("2d");qrcode.width=b.width;qrcode.height=b.height;qrcode.imagedata=a.getImageData(0,0,qrcode.width,qrcode.height);qrcode.result=qrcode.process(a);if(qrcode.callback!=null){qrcode.callback(qrcode.result)}return qrcode.result}else{var c=new Image();c.onload=function(){var i=document.createElement("canvas");var h=i.getContext("2d");var f=document.getElementById("out-canvas");if(f!=null){var g=f.getContext("2d");g.clearRect(0,0,320,240);g.drawImage(c,0,0,320,240)}i.width=c.width;i.height=c.height;h.drawImage(c,0,0);qrcode.width=c.width;qrcode.height=c.height;try{qrcode.imagedata=h.getImageData(0,0,c.width,c.height)}catch(j){qrcode.result="Cross domain image reading not supported in your browser! Save it to your computer then drag and drop the file!";if(qrcode.callback!=null){qrcode.callback(qrcode.result)}return}try{qrcode.result=qrcode.process(h)}catch(j){console.log(j);qrcode.result="error decoding QR Code"}if(qrcode.callback!=null){qrcode.callback(qrcode.result)}};c.src=d}};qrcode.decode_utf8=function(a){return decodeURIComponent(escape(a))};qrcode.process=function(r){var a=new Date().getTime();var c=qrcode.grayScaleToBitmap(qrcode.grayscale());if(qrcode.debug){for(var m=0;m<qrcode.height;m++){for(var n=0;n<qrcode.width;n++){var o=(n*4)+(m*qrcode.width*4);qrcode.imagedata.data[o]=c[n+m*qrcode.width]?0:0;qrcode.imagedata.data[o+1]=c[n+m*qrcode.width]?0:0;qrcode.imagedata.data[o+2]=c[n+m*qrcode.width]?255:0}}r.putImageData(qrcode.imagedata,0,0)}var h=new Detector(c);var q=h.detect();if(qrcode.debug){r.putImageData(qrcode.imagedata,0,0)}var k=Decoder.decode(q.bits);var g=k.DataByte;var l="";for(var f=0;f<g.length;f++){for(var e=0;e<g[f].length;e++){l+=String.fromCharCode(g[f][e])}}var d=new Date().getTime();var b=d-a;console.log(b);return qrcode.decode_utf8(l)};qrcode.getPixel=function(a,b){if(qrcode.width<a){throw"point error"}if(qrcode.height<b){throw"point error"}point=(a*4)+(b*qrcode.width*4);p=(qrcode.imagedata.data[point]*33+qrcode.imagedata.data[point+1]*34+qrcode.imagedata.data[point+2]*33)/100;return p};qrcode.binarize=function(d){var c=new Array(qrcode.width*qrcode.height);for(var e=0;e<qrcode.height;e++){for(var b=0;b<qrcode.width;b++){var a=qrcode.getPixel(b,e);c[b+e*qrcode.width]=a<=d?true:false}}return c};qrcode._em=function(d){var c=4;var k=Math.floor(qrcode.width/c);var j=Math.floor(qrcode.height/c);var f=new Array(c);for(var g=0;g<c;g++){f[g]=new Array(c);for(var e=0;e<c;e++){f[g][e]=new Array(0,0)}}for(var o=0;o<c;o++){for(var a=0;a<c;a++){f[a][o][0]=255;for(var l=0;l<j;l++){for(var n=0;n<k;n++){var h=d[k*a+n+(j*o+l)*qrcode.width];if(h<f[a][o][0]){f[a][o][0]=h}if(h>f[a][o][1]){f[a][o][1]=h}}}}}var m=new Array(c);for(var b=0;b<c;b++){m[b]=new Array(c)}for(var o=0;o<c;o++){for(var a=0;a<c;a++){m[a][o]=Math.floor((f[a][o][0]+f[a][o][1])/2)}}return m};qrcode.grayScaleToBitmap=function(f){var j=qrcode._em(f);var b=j.length;var e=Math.floor(qrcode.width/b);var d=Math.floor(qrcode.height/b);var c=new Array(qrcode.height*qrcode.width);for(var i=0;i<b;i++){for(var a=0;a<b;a++){for(var g=0;g<d;g++){for(var h=0;h<e;h++){c[e*a+h+(d*i+g)*qrcode.width]=(f[e*a+h+(d*i+g)*qrcode.width]<j[a][i])?true:false}}}}return c};qrcode.grayscale=function(){var c=new Array(qrcode.width*qrcode.height);for(var d=0;d<qrcode.height;d++){for(var b=0;b<qrcode.width;b++){var a=qrcode.getPixel(b,d);c[b+d*qrcode.width]=a}}return c};function _ew(a,b){if(a>=0){return a>>b}else{return(a>>b)+(2<<~b)}}Array.prototype.remove=function(c,b){var a=this.slice((b||c)+1||this.length);this.length=c<0?this.length+c:c;return this.push.apply(this,a)};var _gf=3;var _eh=57;var _el=8;var _eg=2;qrcode._er=function(c){function b(l,k){xDiff=l.X-k.X;yDiff=l.Y-k.Y;return Math.sqrt((xDiff*xDiff+yDiff*yDiff))}function d(k,o,n){var m=o.x;var l=o.y;return((n.x-m)*(k.y-l))-((n.y-l)*(k.x-m))}var i=b(c[0],c[1]);var f=b(c[1],c[2]);var e=b(c[0],c[2]);var a,j,h;if(f>=i&&f>=e){j=c[0];a=c[1];h=c[2]}else{if(e>=f&&e>=i){j=c[1];a=c[0];h=c[2]}else{j=c[2];a=c[0];h=c[1]}}if(d(a,j,h)<0){var g=a;a=h;h=g}c[0]=a;c[1]=j;c[2]=h};function _cz(c,a,b){this.x=c;this.y=a;this.count=1;this._aj=b;this.__defineGetter__("_ei",function(){return this._aj});this.__defineGetter__("Count",function(){return this.count});this.__defineGetter__("X",function(){return this.x});this.__defineGetter__("Y",function(){return this.y});this._ek=function(){this.count++};this._ev=function(f,e,d){if(Math.abs(e-this.y)<=f&&Math.abs(d-this.x)<=f){var g=Math.abs(f-this._aj);return g<=1||g/this._aj<=1}return false}}function _es(a){this._go=a[0];this._gu=a[1];this._gr=a[2];this.__defineGetter__("_gp",function(){return this._go});this.__defineGetter__("_gq",function(){return this._gu});this.__defineGetter__("_gs",function(){return this._gr})}function _cc(){this.image=null;this._cv=[];this._ge=false;this._al=new Array(0,0,0,0,0);this._am=null;this.__defineGetter__("_da",function(){this._al[0]=0;this._al[1]=0;this._al[2]=0;this._al[3]=0;this._al[4]=0;return this._al});this._ao=function(f){var b=0;for(var d=0;d<5;d++){var e=f[d];if(e==0){return false}b+=e}if(b<7){return false}var c=Math.floor((b<<_el)/7);var a=Math.floor(c/2);return Math.abs(c-(f[0]<<_el))<a&&Math.abs(c-(f[1]<<_el))<a&&Math.abs(3*c-(f[2]<<_el))<3*a&&Math.abs(c-(f[3]<<_el))<a&&Math.abs(c-(f[4]<<_el))<a};this._an=function(b,a){return(a-b[4]-b[3])-b[2]/2};this._ap=function(a,j,d,g){var c=this.image;var h=qrcode.height;var b=this._da;var f=a;while(f>=0&&c[j+f*qrcode.width]){b[2]++;f--}if(f<0){return NaN}while(f>=0&&!c[j+f*qrcode.width]&&b[1]<=d){b[1]++;f--}if(f<0||b[1]>d){return NaN}while(f>=0&&c[j+f*qrcode.width]&&b[0]<=d){b[0]++;f--}if(b[0]>d){return NaN}f=a+1;while(f<h&&c[j+f*qrcode.width]){b[2]++;f++}if(f==h){return NaN}while(f<h&&!c[j+f*qrcode.width]&&b[3]<d){b[3]++;f++}if(f==h||b[3]>=d){return NaN}while(f<h&&c[j+f*qrcode.width]&&b[4]<d){b[4]++;f++}if(b[4]>=d){return NaN}var e=b[0]+b[1]+b[2]+b[3]+b[4];if(5*Math.abs(e-g)>=2*g){return NaN}return this._ao(b)?this._an(b,f):NaN};this._ej=function(b,a,e,h){var d=this.image;var i=qrcode.width;var c=this._da;var g=b;while(g>=0&&d[g+a*qrcode.width]){c[2]++;g--}if(g<0){return NaN}while(g>=0&&!d[g+a*qrcode.width]&&c[1]<=e){c[1]++;g--}if(g<0||c[1]>e){return NaN}while(g>=0&&d[g+a*qrcode.width]&&c[0]<=e){c[0]++;g--}if(c[0]>e){return NaN}g=b+1;while(g<i&&d[g+a*qrcode.width]){c[2]++;g++}if(g==i){return NaN}while(g<i&&!d[g+a*qrcode.width]&&c[3]<e){c[3]++;g++}if(g==i||c[3]>=e){return NaN}while(g<i&&d[g+a*qrcode.width]&&c[4]<e){c[4]++;g++}if(c[4]>=e){return NaN}var f=c[0]+c[1]+c[2]+c[3]+c[4];if(5*Math.abs(f-h)>=h){return NaN}return this._ao(c)?this._an(c,g):NaN};this._cu=function(c,f,e){var d=c[0]+c[1]+c[2]+c[3]+c[4];var n=this._an(c,e);var b=this._ap(f,Math.floor(n),c[2],d);if(!isNaN(b)){n=this._ej(Math.floor(n),Math.floor(b),c[2],d);if(!isNaN(n)){var l=d/7;var m=false;var h=this._cv.length;for(var g=0;g<h;g++){var a=this._cv[g];if(a._ev(l,b,n)){a._ek();m=true;break}}if(!m){var k=new _cz(n,b,l);this._cv.push(k);if(this._am!=null){this._am._ep(k)}}return true}}return false};this._ee=function(){var a=this._cv.length;if(a<3){throw"Couldn't find enough finder patterns"}if(a>3){var b=0;for(var c=0;c<a;c++){b+=this._cv[c]._ei}var d=b/a;for(var c=0;c<this._cv.length&&this._cv.length>3;c++){var e=this._cv[c];if(Math.abs(e._ei-d)>0.2*d){this._cv.remove(c);c--}}}if(this._cv.length>3){this._cv.sort(function(g,f){if(g.count>f.count){return -1}if(g.count<f.count){return 1}return 0})}return new Array(this._cv[0],this._cv[1],this._cv[2])};this._eq=function(){var b=this._cv.length;if(b<=1){return 0}var c=null;for(var d=0;d<b;d++){var a=this._cv[d];if(a.Count>=_eg){if(c==null){c=a}else{this._ge=true;return Math.floor((Math.abs(c.X-a.X)-Math.abs(c.Y-a.Y))/2)}}}return 0};this._cx=function(){var g=0;var c=0;var a=this._cv.length;for(var d=0;d<a;d++){var f=this._cv[d];if(f.Count>=_eg){g++;c+=f._ei}}if(g<3){return false}var e=c/a;var b=0;for(var d=0;d<a;d++){f=this._cv[d];b+=Math.abs(f._ei-e)}return b<=0.05*c};this._ce=function(e){var o=false;this.image=e;var n=qrcode.height;var k=qrcode.width;var a=Math.floor((3*n)/(4*_eh));if(a<_gf||o){a=_gf}var g=false;var d=new Array(5);for(var h=a-1;h<n&&!g;h+=a){d[0]=0;d[1]=0;d[2]=0;d[3]=0;d[4]=0;var b=0;for(var f=0;f<k;f++){if(e[f+h*qrcode.width]){if((b&1)==1){b++}d[b]++}else{if((b&1)==0){if(b==4){if(this._ao(d)){var c=this._cu(d,h,f);if(c){a=2;if(this._ge){g=this._cx()}else{var m=this._eq();if(m>d[2]){h+=m-d[2]-a;f=k-1}}}else{do{f++}while(f<k&&!e[f+h*qrcode.width]);f--}b=0;d[0]=0;d[1]=0;d[2]=0;d[3]=0;d[4]=0}else{d[0]=d[2];d[1]=d[3];d[2]=d[4];d[3]=1;d[4]=0;b=3}}else{d[++b]++}}else{d[b]++}}}if(this._ao(d)){var c=this._cu(d,h,k);if(c){a=d[0];if(this._ge){g=_cx()}}}}var l=this._ee();qrcode._er(l);return new _es(l)}}function _ai(c,a,b){this.x=c;this.y=a;this.count=1;this._aj=b;this.__defineGetter__("_ei",function(){return this._aj});this.__defineGetter__("Count",function(){return this.count});this.__defineGetter__("X",function(){return Math.floor(this.x)});this.__defineGetter__("Y",function(){return Math.floor(this.y)});this._ek=function(){this.count++};this._ev=function(f,e,d){if(Math.abs(e-this.y)<=f&&Math.abs(d-this.x)<=f){var g=Math.abs(f-this._aj);return g<=1||g/this._aj<=1}return false}}function _ak(g,c,b,f,a,e,d){this.image=g;this._cv=new Array();this.startX=c;this.startY=b;this.width=f;this.height=a;this._ef=e;this._al=new Array(0,0,0);this._am=d;this._an=function(i,h){return(h-i[2])-i[1]/2};this._ao=function(l){var k=this._ef;var h=k/2;for(var j=0;j<3;j++){if(Math.abs(k-l[j])>=h){return false}}return true};this._ap=function(h,r,l,o){var k=this.image;var q=qrcode.height;var j=this._al;j[0]=0;j[1]=0;j[2]=0;var n=h;while(n>=0&&k[r+n*qrcode.width]&&j[1]<=l){j[1]++;n--}if(n<0||j[1]>l){return NaN}while(n>=0&&!k[r+n*qrcode.width]&&j[0]<=l){j[0]++;n--}if(j[0]>l){return NaN}n=h+1;while(n<q&&k[r+n*qrcode.width]&&j[1]<=l){j[1]++;n++}if(n==q||j[1]>l){return NaN}while(n<q&&!k[r+n*qrcode.width]&&j[2]<=l){j[2]++;n++}if(j[2]>l){return NaN}var m=j[0]+j[1]+j[2];if(5*Math.abs(m-o)>=2*o){return NaN}return this._ao(j)?this._an(j,n):NaN};this._cu=function(l,o,n){var m=l[0]+l[1]+l[2];var u=this._an(l,n);var k=this._ap(o,Math.floor(u),2*l[1],m);if(!isNaN(k)){var t=(l[0]+l[1]+l[2])/3;var r=this._cv.length;for(var q=0;q<r;q++){var h=this._cv[q];if(h._ev(t,k,u)){return new _ai(u,k,t)}}var s=new _ai(u,k,t);this._cv.push(s);if(this._am!=null){this._am._ep(s)}}return null};this.find=function(){var q=this.startX;var t=this.height;var r=q+f;var s=b+(t>>1);var m=new Array(0,0,0);for(var k=0;k<t;k++){var o=s+((k&1)==0?((k+1)>>1):-((k+1)>>1));m[0]=0;m[1]=0;m[2]=0;var n=q;while(n<r&&!g[n+qrcode.width*o]){n++}var h=0;while(n<r){if(g[n+o*qrcode.width]){if(h==1){m[h]++}else{if(h==2){if(this._ao(m)){var l=this._cu(m,o,n);if(l!=null){return l}}m[0]=m[2];m[1]=1;m[2]=0;h=1}else{m[++h]++}}}else{if(h==1){h++}m[h]++}n++}if(this._ao(m)){var l=this._cu(m,o,r);if(l!=null){return l}}}if(!(this._cv.length==0)){return this._cv[0]}throw"Couldn't find enough alignment patterns"}}function QRCodeDataBlockReader(c,a,b){this._ed=0;this._cw=7;this.dataLength=0;this.blocks=c;this._en=b;if(a<=9){this.dataLengthMode=0}else{if(a>=10&&a<=26){this.dataLengthMode=1}else{if(a>=27&&a<=40){this.dataLengthMode=2}}}this._gd=function(f){var k=0;if(f<this._cw+1){var m=0;for(var e=0;e<f;e++){m+=(1<<e)}m<<=(this._cw-f+1);k=(this.blocks[this._ed]&m)>>(this._cw-f+1);this._cw-=f;return k}else{if(f<this._cw+1+8){var j=0;for(var e=0;e<this._cw+1;e++){j+=(1<<e)}k=(this.blocks[this._ed]&j)<<(f-(this._cw+1));this._ed++;k+=((this.blocks[this._ed])>>(8-(f-(this._cw+1))));this._cw=this._cw-f%8;if(this._cw<0){this._cw=8+this._cw}return k}else{if(f<this._cw+1+16){var j=0;var h=0;for(var e=0;e<this._cw+1;e++){j+=(1<<e)}var g=(this.blocks[this._ed]&j)<<(f-(this._cw+1));this._ed++;var d=this.blocks[this._ed]<<(f-(this._cw+1+8));this._ed++;for(var e=0;e<f-(this._cw+1+8);e++){h+=(1<<e)}h<<=8-(f-(this._cw+1+8));var l=(this.blocks[this._ed]&h)>>(8-(f-(this._cw+1+8)));k=g+d+l;this._cw=this._cw-(f-8)%8;if(this._cw<0){this._cw=8+this._cw}return k}else{return 0}}}};this.NextMode=function(){if((this._ed>this.blocks.length-this._en-2)){return 0}else{return this._gd(4)}};this.getDataLength=function(d){var e=0;while(true){if((d>>e)==1){break}e++}return this._gd(qrcode._eo[this.dataLengthMode][e])};this.getRomanAndFigureString=function(h){var f=h;var g=0;var j="";var d=new Array("0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"," ","$","%","*","+","-",".","/",":");do{if(f>1){g=this._gd(11);var i=Math.floor(g/45);var e=g%45;j+=d[i];j+=d[e];f-=2}else{if(f==1){g=this._gd(6);j+=d[g];f-=1}}}while(f>0);return j};this.getFigureString=function(f){var d=f;var e=0;var g="";do{if(d>=3){e=this._gd(10);if(e<100){g+="0"}if(e<10){g+="0"}d-=3}else{if(d==2){e=this._gd(7);if(e<10){g+="0"}d-=2}else{if(d==1){e=this._gd(4);d-=1}}}g+=e}while(d>0);return g};this.get8bitByteArray=function(g){var e=g;var f=0;var d=new Array();do{f=this._gd(8);d.push(f);e--}while(e>0);return d};this.getKanjiString=function(j){var g=j;var i=0;var h="";do{i=_gd(13);var e=i%192;var f=i/192;var k=(f<<8)+e;var d=0;if(k+33088<=40956){d=k+33088}else{d=k+49472}h+=String.fromCharCode(d);g--}while(g>0);return h};this.__defineGetter__("DataByte",function(){var g=new Array();var e=1;var f=2;var d=4;var n=8;do{var k=this.NextMode();if(k==0){if(g.length>0){break}else{throw"Empty data block"}}if(k!=e&&k!=f&&k!=d&&k!=n){throw"Invalid mode: "+k+" in (block:"+this._ed+" bit:"+this._cw+")"}dataLength=this.getDataLength(k);if(dataLength<1){throw"Invalid data length: "+dataLength}switch(k){case e:var l=this.getFigureString(dataLength);var i=new Array(l.length);for(var h=0;h<l.length;h++){i[h]=l.charCodeAt(h)}g.push(i);break;case f:var l=this.getRomanAndFigureString(dataLength);var i=new Array(l.length);for(var h=0;h<l.length;h++){i[h]=l.charCodeAt(h)}g.push(i);break;case d:var m=this.get8bitByteArray(dataLength);g.push(m);break;case n:var l=this.getKanjiString(dataLength);g.push(l);break}}while(true);return g})};
  </script> 
  <script>
    var gCtx = null;
    var gCanvas = null;
    var imageData = null;
    var c=0;
    var stype=0;
    var webkit=false;
    var v=null;

    function initCanvas(ww,hh)
    {
        gCanvas = document.getElementById("qr-canvas");
        var w = ww;
        var h = hh;
        gCanvas.style.width = w + "px";
        gCanvas.style.height = h + "px";
        gCanvas.width = w;
        gCanvas.height = h;
        gCtx = gCanvas.getContext("2d");
        gCtx.clearRect(0, 0, w, h);
        imageData = gCtx.getImageData( 0,0,320,240);
    }

    function htmlEntities(str) {
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function read(a)
    {
        var html="<br>";
        if(a.indexOf("http://") === 0 || a.indexOf("https://") === 0)
            html+="<a target='_blank' href='"+a+"'>"+a+"</a><br>";
        html+="<b>"+htmlEntities(a)+"</b><br><br>";
        document.getElementById("result").innerHTML=html;
    }    

    function isCanvasSupported(){
        var elem = document.createElement('canvas');
        return !!(elem.getContext && elem.getContext('2d'));
    }

    function load()
    {
        if(isCanvasSupported() && window.File && window.FileReader)
        {
            initCanvas(90,70);
            qrcode.callback = read;
            document.getElementById("mainbody").style.display="inline";
        }
        else
        {
            document.getElementById("mainbody").style.display="inline";
            document.getElementById("mainbody").innerHTML='<p id="mp1">QR code scanner for HTML5 capable browsers</p><br>'+
            '<br><p id="mp2">sorry your browser is not supported</p><br><br>'+
            '<p id="mp1">try <a href="http://www.mozilla.com/firefox"><img src="firefox.png"/></a> or <a href="http://chrome.google.com"><img src="chrome_logo.gif"/></a> or <a href="http://www.opera.com"><img src="Opera-logo.png"/></a></p>';
        }
    }

    function setimg()
    {
        document.getElementById("result").innerHTML="";
        //if(stype==2)
            //return;
        var qrfile = document.getElementById('qrimage').src;
        gCtx.clearRect(0, 0, gCanvas.width, gCanvas.height);
        qrcode.decode(qrfile);
        stype=2;
    }
  </script>
  <script>
   function previewFile(){
       load();
       setimg();
       var preview = document.querySelector('img'); //selects the query named img
       var file    = document.querySelector('input[type=file]').files[0]; //sames as here
       var reader  = new FileReader();

       reader.onloadend = function () {
           preview.src = reader.result;
       }

       if (file) {
           reader.readAsDataURL(file); //reads the data as a URL
       } else {
           preview.src = "";
       }
  }

  previewFile();  //calls the function named previewFile()
  </script>
 </head> 
 <body> 
   <div > 
 
     <div id="mainbody"> 
        ''' + ''' <img src="data:image/png;base64,%s" height="80" id="qrimage" alt="Image preview..." style="visibility:hidden;"> '''%str(link) + ''' </div> 
      </div> 
      <div id="result"></div> 
         <canvas id="qr-canvas" width="90" height="70"></canvas> 
     </div> 
     </body>
     </html> '''
            return {'value': {'youtube_show': content}}
        return {'value': {}}
    
    def write(self, cr, uid, ids, vals, context={}):
        dhl_id = 0
        #    For youtube
#         if vals.get('youtube_link', False):
#             if vals['youtube_link'] != '':
        content = self.onchange_link(cr, uid, ids, self.browse(cr, uid, ids)[0].youtube_link)
        vals.update({'youtube_show':content['value']['youtube_show']})
                #vals.update({'youtube_show': '<iframe width="600" height="300" src="%s" frameborder="0" allowfullscreen=""></iframe>'%vals['youtube_link']})
        #    End Youtube
        for rc in self.browse(cr, uid, ids):
            inv_ids = rc.inv_ids and [x.id for x in rc.inv_ids] or []
            dhl_id = rc.dhl_id and rc.dhl_id.id or 0
        result = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids):            
            if record.is_dhl and vals.get('inv_ids', False):# DHL
                temp = vals.get('inv_ids')[0][2]
                for idd in inv_ids:
                    if idd not in temp:#    Delete invoice
                        sql_d = ''' Update account_invoice set dhl_id = null where id = %s'''%idd
                        cr.execute(sql_d)
                if len(temp)>0:
                    temp = tuple(temp + [-1])
                    sql_u = ''' Update account_invoice set dhl_id = %s where id in %s'''%(record.id, temp)
                    cr.execute(sql_u)
            elif not record.is_dhl:
                print 'dhl_id  ==  ', dhl_id, ' record.id ', record.id 
                if dhl_id:# Delete old
                    sql_del = ''' Delete from dhl_invoice_rel where dhl_id = %s and inv_id = %s '''%(dhl_id, record.id)
                    cr.execute(sql_del)
                if vals.get('dhl_id', False):
                    sql_ins = ''' Insert into dhl_invoice_rel values (%s, %s) '''%(vals['dhl_id'], record.id)
                    sql_del = cr.execute(sql_ins)
        return result
        
account_invoice()
