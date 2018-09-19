$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        }
    },
    timeout : 15000
});

$('form').on('submit', function() {
    $(document).find('#loading').show();
});

$('#delete_button').on('click', function() {
    if (!window.confirm('削除してよろしいですか？')) {
        return false;
    }
});

$('body').append('<div id="loading" class="loading"></div>');

$('.header_menu_button').on('click', function() {
    $('#menu').toggleClass('_open');
});


if ($('#input_image_add_button').length != 0) {
    $('#input_image_add_button').on('click', function() {
        $('#upload').click();
    });
    $('#upload').on('change', function(event) {
        $('#image_upload').off('submit');
        $('#image_upload').on('submit', function(e) {

            e.stopPropagation();
            e.preventDefault();

            $('#loading').show();

            var maxWidth = 800;
            var maxHeight = 800;

            var file = event.target.files[0];
            if (!file.type.match(/^image\/(png|jpeg|gif)$/)) return;

            var img = new Image();
            var reader = new FileReader();

            reader.onload = function(e) {

                var data = e.target.result;

                img.onload = function() {

                    var iw = img.naturalWidth, ih = img.naturalHeight;
                    var width = iw, height = ih;

                    var orientation;

                    // JPEGの場合には、EXIFからOrientation（回転）情報を取得
                    if (data.split(',')[0].match('jpeg')) {
                        orientation = getOrientation(data);
                    }
                    // JPEG以外や、JPEGでもEXIFが無い場合などには、標準の値に設定
                    orientation = orientation || 1;

                    // ９０度回転など、縦横が入れ替わる場合には事前に最大幅、高さを入れ替えておく
                    if (orientation > 4) {
                        var tmpMaxWidth = maxWidth;
                        maxWidth = maxHeight;
                        maxHeight = tmpMaxWidth;
                    }

                    if(width > maxWidth || height > maxHeight) {
                        var ratio = width/maxWidth;
                        if(ratio <= height/maxHeight) {
                            ratio = height/maxHeight;
                        }
                        width = Math.floor(img.width/ratio);
                        height = Math.floor(img.height/ratio);
                    }

                    var canvas = document.createElement('canvas');
                    var ctx = canvas.getContext('2d');
                    ctx.save();

                    // EXIFのOrientation情報からCanvasを回転させておく
                    transformCoordinate(canvas, width, height, orientation);

                    // iPhoneのサブサンプリング問題の回避
                    // see http://d.hatena.ne.jp/shinichitomita/20120927/1348726674
                    var subsampled = detectSubsampling(img);
                    if (subsampled) {
                        iw /= 2;
                        ih /= 2;
                    }
                    var d = 1024; // size of tiling canvas
                    var tmpCanvas = document.createElement('canvas');
                    tmpCanvas.width = tmpCanvas.height = d;
                    var tmpCtx = tmpCanvas.getContext('2d');
                    var vertSquashRatio = detectVerticalSquash(img, iw, ih);
                    var dw = Math.ceil(d * width / iw);
                    var dh = Math.ceil(d * height / ih / vertSquashRatio);
                    var sy = 0;
                    var dy = 0;
                    while (sy < ih) {
                        var sx = 0;
                        var dx = 0;
                        while (sx < iw) {
                            tmpCtx.clearRect(0, 0, d, d);
                            tmpCtx.drawImage(img, -sx, -sy);
                            // 何度もImageDataオブジェクトとCanvasの変換を行ってるけど、
                            // Orientation関連で仕方ない
                            // 本当はputImageDataであれば良いけどOrientation効かない
                            var imageData = tmpCtx.getImageData(0, 0, d, d);
                            var resampled = resample_hermite(imageData, d, d, dw, dh);
                            ctx.drawImage(resampled, 0, 0, dw, dh, dx, dy, dw, dh);
                            sx += d;
                            dx += dw;
                        }
                        sy += d;
                        dy += dh;
                    }
                    ctx.restore();
                    tmpCanvas = tmpCtx = null;
                    var displaySrc = ctx.canvas.toDataURL('image/jpeg', .4);
                    var fd = new FormData();
                    fd.append('barcode_base64', displaySrc);

                    $.ajax({
                        type: 'POST',
                        url: '/api/barcode',
                        cache: false,
                        data: fd,
                        processData: false,
                        contentType: false
                    }).done(function(data) {
                        $.each(data.products, function(i, product) {
                            $('#product_list').append('<li>' + '<strong>' + product.product_name + '</strong><br>' + product.brand + '<br>' + product.model_number + '<br>' + product.category.name + '<br>' + product.jan_code + '</li>');
                        });

                    }).fail(function(jqXHR) {
                        if (jqXHR.status !== 404) {
                            $('.header_status_text').text('通信エラー');
                            $('.header_status').addClass('_show _error');
                        } else {
                            $('.barcode_status').append('<p>' + jqXHR.responseJSON.message + '</p>');
                        }

                    }).always(function() {
                        $('input[name="barcode_base64"]').val('');
                        $('#loading').hide();
                        setTimeout(function() {
                            $('.barcode_status p').remove();
                            $('.header_status_text').text('');
                            $('.header_status').removeClass('_show _success _error');
                        }, 2000);
                    });
                }
                img.src = data;

            }
            reader.readAsDataURL(file);
        });

        $('#image_upload').trigger('submit');

    });
}

// hermite filterかけてジャギーを削除する
function resample_hermite(img, W, H, W2, H2){
    var canvas = document.createElement('canvas');
    canvas.width = W2;
    canvas.height = H2;
    var ctx = canvas.getContext('2d');
    var img2 = ctx.createImageData(W2, H2);
    var data = img.data;
    var data2 = img2.data;
    var ratio_w = W / W2;
    var ratio_h = H / H2;
    var ratio_w_half = Math.ceil(ratio_w/2);
    var ratio_h_half = Math.ceil(ratio_h/2);
    for(var j = 0; j < H2; j++){
        for(var i = 0; i < W2; i++){
            var x2 = (i + j*W2) * 4;
            var weight = 0;
            var weights = 0;
            var gx_r = 0, gx_g = 0,  gx_b = 0, gx_a = 0;
            var center_y = (j + 0.5) * ratio_h;
            for(var yy = Math.floor(j * ratio_h); yy < (j + 1) * ratio_h; yy++){
                var dy = Math.abs(center_y - (yy + 0.5)) / ratio_h_half;
                var center_x = (i + 0.5) * ratio_w;
                var w0 = dy*dy;
                for(var xx = Math.floor(i * ratio_w); xx < (i + 1) * ratio_w; xx++){
                    var dx = Math.abs(center_x - (xx + 0.5)) / ratio_w_half;
                    var w = Math.sqrt(w0 + dx*dx);
                    if(w >= -1 && w <= 1){
                        weight = 2 * w*w*w - 3*w*w + 1;
                        if(weight > 0){
                            dx = 4*(xx + yy*W);
                            gx_r += weight * data[dx];
                            gx_g += weight * data[dx + 1];
                            gx_b += weight * data[dx + 2];
                            gx_a += weight * data[dx + 3];
                            weights += weight;
                        }
                    }
                }
            }
            data2[x2] = gx_r / weights;
            data2[x2 + 1] = gx_g / weights;
            data2[x2 + 2] = gx_b / weights;
            data2[x2 + 3] = gx_a / weights;
        }
    }
    ctx.putImageData(img2, 0, 0);
    return canvas;
};

// JPEGのEXIFからOrientationのみを取得する
function getOrientation(imgDataURL){
    var byteString = atob(imgDataURL.split(',')[1]);
    var orientaion = byteStringToOrientation(byteString);
    return orientaion;

    function byteStringToOrientation(img){
        var head = 0;
        var orientation;
        while (1){
            if (img.charCodeAt(head) == 255 & img.charCodeAt(head + 1) == 218) {break;}
            if (img.charCodeAt(head) == 255 & img.charCodeAt(head + 1) == 216) {
                head += 2;
            }
            else {
                var length = img.charCodeAt(head + 2) * 256 + img.charCodeAt(head + 3);
                var endPoint = head + length + 2;
                if (img.charCodeAt(head) == 255 & img.charCodeAt(head + 1) == 225) {
                    var segment = img.slice(head, endPoint);
                    var bigEndian = segment.charCodeAt(10) == 77;
                    if (bigEndian) {
                        var count = segment.charCodeAt(18) * 256 + segment.charCodeAt(19);
                    } else {
                        var count = segment.charCodeAt(18) + segment.charCodeAt(19) * 256;
                    }
                    for (var i=0;i<count;i++){
                        var field = segment.slice(20 + 12 * i, 32 + 12 * i);
                        if ((bigEndian && field.charCodeAt(1) == 18) || (!bigEndian && field.charCodeAt(0) == 18)) {
                            orientation = bigEndian ? field.charCodeAt(9) : field.charCodeAt(8);
                        }
                    }
                    break;
                }
                head = endPoint;
            }
            if (head > img.length){break;}
        }
        return orientation;
    }
}

// iPhoneのサブサンプリングを検出
function detectSubsampling(img) {
    var iw = img.naturalWidth, ih = img.naturalHeight;
    if (iw * ih > 1024 * 1024) {
        var canvas = document.createElement('canvas');
        canvas.width = canvas.height = 1;
        var ctx = canvas.getContext('2d');
        ctx.drawImage(img, -iw + 1, 0);
        return ctx.getImageData(0, 0, 1, 1).data[3] === 0;
    } else {
        return false;
    }
}

// iPhoneの縦画像でひしゃげて表示される問題の回避
function detectVerticalSquash(img, iw, ih) {
    var canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = ih;
    var ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);
    var data = ctx.getImageData(0, 0, 1, ih).data;
    var sy = 0;
    var ey = ih;
    var py = ih;
    while (py > sy) {
        var alpha = data[(py - 1) * 4 + 3];
        if (alpha === 0) {
            ey = py;
        } else {
            sy = py;
        }
        py = (ey + sy) >> 1;
    }
    var ratio = (py / ih);
    return (ratio===0)?1:ratio;
}

function transformCoordinate(canvas, width, height, orientation) {
    if (orientation > 4) {
        canvas.width = height;
        canvas.height = width;
    } else {
        canvas.width = width;
        canvas.height = height;
    }
    var ctx = canvas.getContext('2d');
    switch (orientation) {
        case 2:
            // horizontal flip
            ctx.translate(width, 0);
            ctx.scale(-1, 1);
            break;
        case 3:
            // 180 rotate left
            ctx.translate(width, height);
            ctx.rotate(Math.PI);
            break;
        case 4:
            // vertical flip
            ctx.translate(0, height);
            ctx.scale(1, -1);
            break;
        case 5:
            // vertical flip + 90 rotate right
            ctx.rotate(0.5 * Math.PI);
            ctx.scale(1, -1);
            break;
        case 6:
            // 90 rotate right
            ctx.rotate(0.5 * Math.PI);
            ctx.translate(0, -height);
            break;
        case 7:
            // horizontal flip + 90 rotate right
            ctx.rotate(0.5 * Math.PI);
            ctx.translate(width, -height);
            ctx.scale(-1, 1);
            break;
        case 8:
            // 90 rotate left
            ctx.rotate(-0.5 * Math.PI);
            ctx.translate(-width, 0);
            break;
        default:
            break;
    }
}

$('#csv_input').on('change', function(event) {
    $('#csv_upload').off('submit');
    $('#csv_upload').on('submit', function(e) {

        var file = event.target.files[0];
        if (!file.type.match(/^text\/csv$/)) {
            e.stopPropagation();
            e.preventDefault();
            alert('csvファイルを選択してください。')
        };

    });

    $('#csv_upload').trigger('submit');

});
