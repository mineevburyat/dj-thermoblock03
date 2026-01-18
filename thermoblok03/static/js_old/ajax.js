$("#btn_ajax").click(
    function(e){
        e.preventDefault();
        sendAjaxForm('result_div', 'form', '/feedback');
        return false; 
    }
);
function sendAjaxForm(result_form, ajax_form, url) {
    var hasEmpty = false;
    // Перебираем все поля формы
    $('#form').find('input').each(function() {
    if ($(this).prop('required') & !$(this).val())  {
        $(this).prop('placeholder') = 'необходимо заполнить'
        }
    else {
        var data_ajax = $("#"+ajax_form).serialize();
        console.log(data_ajax);  
        $.ajax({
            url:     url, //url страницы (action_ajax_form.php)
            type:     "POST", 
            dataType: "html", 
            data: data_ajax,  
            success: function(response) { //Данные отправлены успешно
                result = $.parseJSON(response);
                console.log(result);
                if (result.status) {
                    $(result_form).html('Отправлено успешно');
                }
                else {
                    if (result.errors.name) {
                        $('#form_name_err').html(result.errors.name)
                    }
                    if (result.errors.phone) {
                        $('#form_phone_err').html(result.errors.phone)
                    } 
                    if (result.errors.captcha) {
                        $('#form_captcha_err').html(result.errors.captcha)
                    }
                }
            },
            error: function(response) { // Данные не отправлены
                console.log(response);
                $(result_form).html('Ошибка. Данные не отправлены.');
            }
            });
        }
    });

    
    
}