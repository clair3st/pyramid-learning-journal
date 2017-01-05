$(document).ready(function(){
    var creator = $(".create");
    creator.on("click", function(){
        // send ajax request to create this entry
        $.ajax({
            url: 'newpost/' + $(this).attr("data"),
            data: {
                "title": "some name",
                "body": "some company"
            }
            success: function(){
                console.log("attempted to add");
            }
        });
    });
});
