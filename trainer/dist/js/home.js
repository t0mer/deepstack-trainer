$(document).on('change', '.btn-file :file', function () {
    var input = $(this),
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
    input.trigger('fileselect', [label]);
});


$('.btn-file :file').on('fileselect', function (event, label) {
    var input = $(this).parents('.input-group').find(':text'),
        log = label;
    if (input.length) {
        input.val(log);
    } else {
        if (log) alert(log);
    }
});


function readURL(input, id) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $(id).attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
}


$(document).ready(function () {

    $(".imgfile").change(function () {
        var action = $(this).attr('id').split("-")[0];
        readURL(this, '#' + action + '-img');
    });

    $('.btn-post').click(function () {
        var action = $(this).attr('id').split("-")[0];
        var form_data = new FormData($('#' + action + '-form')[0]);
        $.ajax({
            type: 'POST',
            url: '/' + action,
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                try {
                    data = JSON.parse(data)
                    if (data.success == "false") {
                        Swal.fire({
                            title: 'Error!',
                            text: data.error,
                            icon: 'error',
                            confirmButtonText: 'Ok'
                        })
                    }
                    if (data.success == "true") {
                        Swal.fire({
                            title: 'Success!',
                            text: data.message,
                            icon: 'success',
                            confirmButtonText: 'Ok'
                        }).then((result) => {
                            if (result.isConfirmed) {
                                $('#' + action + '-img').attr('src', './img/avatar.png');
                                $("#" + action + "-form :input").each(function () {
                                    if ($(this).is(":button")) {
                                    }
                                    else {
                                        $(this).val('');
                                    }
                                });
                            } else if (result.isDenied) {
                            }
                        })
                    }
                }
                catch (err) {
                    Swal.fire({
                        title: 'Error!',
                        text: err,
                        icon: 'error',
                        confirmButtonText: 'Ok'
                    })
                }
            },
        });
    });
});