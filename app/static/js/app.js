$(function() {
  var nr = 0;
  $(".draggable").draggable();

  $('.droppable').on({
    'dragover dragenter': function(e) {
      e.preventDefault();
      e.stopPropagation();
    },
    'drop': function(e, ui) {
      //console.log(e.originalEvent instanceof DragEvent);

      image = $(this).find(".file")
      $(image).html("")
      img_id = $(this).attr("data-img-id")
      var dataTransfer = e.originalEvent.dataTransfer;
      if (dataTransfer && dataTransfer.files.length) {
        e.preventDefault();
        e.stopPropagation();
        $.each(dataTransfer.files, function(i, file) {
          var reader = new FileReader();
          reader.onload = $.proxy(function(file, $fileList, event) {
            var img = file.type.match('image.*') ? "<img  id=\"img"+img_id+"\" height=\"200\" src='" + event.target.result + "' /> " : "";
            $fileList.prepend($("<span>").append(img));
          }, this, file, $(image));
          reader.readAsDataURL(file);
        });
      }
      $(this).addClass("ui-state-highlight").find("p").html("Dropped!");
    }
  });

});


$(".swap-btn").click(function(){
    img1 = $("#img1").attr("src")
    img2 = $("#img2").attr("src")
    $("#output").html("Swaping... please wait")
     $.ajax({
        url: "/swap",
        data: {"img1": img1, "img2":img2},
        success: function(data) {
            $("#output").html("<img  id=\"output\" height=\"500\" src='data:image/jpeg;base64," + data + "' /> ")
        },
        error: function(xhr, status, error) {
            $("#output").html("<br><span class='alert alert-danger'>"+error+'</span>')
        },
       type: 'POST'
    });
    return false;

})