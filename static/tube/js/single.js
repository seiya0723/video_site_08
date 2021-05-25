window.addEventListener("load" , function (){

    $("#single_video_comments_submit").on("click",function(){ comments_submit(); });
    single_video_comments_form_initialize();

    $(document).on("click",".rating_good",function(){ rate_submit(true); });
    $(document).on("click",".rating_bad",function(){ rate_submit(false); });

    $(document).on("click","#mylist_submit",function(){ mylist_submit(); });



    const video   = document.querySelector("video");
    video.addEventListener("volumechange",(event) => {
        document.cookie = "volume=" + decodeURIComponent(event.target.volume) + ";Path=/single;SameSite=strict";
    });
 
    set_video_volume();
    
});

function set_video_volume(){

    let cookies         = document.cookie;
    console.log(cookies);

    let cookiesArray    = cookies.split(';');
    let volume          = 0;

    for(let c of cookiesArray) {
        console.log(c);

        let cArray = c.split('=');
        if( cArray[0] === "volume"){
            volume  = Number(cArray[1]);
            console.log(volume);
            break;
        }
    }

    const video     = document.querySelector("video");
    video.volume    = volume;
}

function comments_submit(){

    let form_elem   = "#single_video_comments_form";

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = $(form_elem).prop("method");

    for (let v of data.entries() ){ console.log(v); }

    $.ajax({
        url: url,
        type: method,
        data: data,
        processData: false,
        contentType: false,
        dataType: 'json'
    }).done( function(data, status, xhr ) { 

        if (data.error){
            $("#comments_message").addClass("upload_message_error");
            $("#comments_message").removeClass("upload_message_success");
        }
        else{
            $("#comments_message").addClass("upload_message_success");
            $("#comments_message").removeClass("upload_message_error");
            single_video_comments_form_initialize();

            $("#video_comments_area").html(data.content);
        }

        $("#comments_message").text(data.message)

        console.log(data);

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });

}
function single_video_comments_form_initialize() {
    $("[name='content']").val("");
}


function rate_submit(rate){

    console.log(rate);


    let form_elem   = ".single_video_rating_content";

    let data    = JSON.stringify({ "flag":rate });
    let url     = $(form_elem).prop("action");
    let method  = "PATCH";

    $.ajax({
        url: url,
        type: method,
        contentType : 'application/json; charset=utf-8',
        enctype     : "multipart/form-data",
        data: data,
    }).done( function(data, status, xhr ) { 

        if (data.error){
        }
        else{
            $("#single_video_rating_area").html(data.content);
        }

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });


}

function mylist_submit(id){

    let form_elem   = "#mylist_form_area";

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = $(form_elem).prop("method");

    for (let v of data.entries() ){ console.log(v); }

    $.ajax({
        url: url,
        type: method,
        data: data,
        processData: false,
        contentType: false,
        dataType: 'json'
    }).done( function(data, status, xhr ) { 

        if (data.error){
            $("#mylist_message").addClass("upload_message_error");
            $("#mylist_message").removeClass("upload_message_success");
        }
        else{
            $("#mylist_message").addClass("upload_message_success");
            $("#mylist_message").removeClass("upload_message_error");
        }

        $("#mylist_message").text(data.message)


        console.log(data);

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });

}
