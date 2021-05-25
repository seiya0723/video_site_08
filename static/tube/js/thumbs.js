window.addEventListener("load" , function (){

    //動画選択されたときの再生処理
    (function localFileVideoPlayerInit(global) {

        //global.URLが存在する場合はglobal.URLを、存在しない場合はglobal.webkitURLを代入する。(参照: https://developer.mozilla.org/ja/docs/Web/JavaScript/Guide/Expressions_and_Operators#logical_operators )
        let URL = global.URL || global.webkitURL;

        //動画選択時に再生する
        let playSelectedFile = function playSelectedFileInit(event) {

            let file        = event.target.files[0];
            let type        = file.type;
            let videoNode   = document.querySelector('#thumbnail_video');

            // 再生できないものならreturnで終わる
            if ( videoNode.canPlayType(type) === '' ){ return; }

            videoNode.src   = URL.createObjectURL(file);

            //TODO:読み込み終了後にキャプチャを実行したい
            //capture();
        };

        // ファイルが選択されたときのイベントハンドラ
        let inputNode = document.querySelector('#upload_form_video');
        if (inputNode){
            inputNode.addEventListener('change', playSelectedFile, false);
        }

    }(window));

    //キャプチャーボタンが押されたときのサムネイル自動生成処理
    function capture() {

        //キャンバスタグ、ビデオタグ等、必要な要素を抜き取る
        let cEle    = document.querySelector('#canvas');
        let cCtx    = cEle.getContext('2d');
        let vEle    = document.querySelector('#thumbnail_video');

        //サムネイルのサイズは上限300X300とする
        let video_w = vEle.videoWidth;
        let video_h = vEle.videoHeight;

        let mag = 0;
        if ( video_w > video_h ){
            mag = 300 / video_w;
        }
        else{
            mag = 300 / video_h;
        }

        // canvasに関数実行時の動画のフレームを描画
        // 一定値を下回るまで高さと横幅を削る。
        cEle.width  = vEle.videoWidth  * mag;
        cEle.height = vEle.videoHeight * mag;       

        cCtx.scale(mag,mag);
        cCtx.drawImage(vEle, 0, 0);

        //console.log(cEle.toDataURL('image/png'));

    }

    //キャプチャーボタンが押されたときに発動するイベントハンドラ
    let captureButton   = document.querySelector('#thumbnail_button');
    if (captureButton){
        captureButton.addEventListener('click', capture, false);
    }

});
