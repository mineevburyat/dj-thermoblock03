$(document).ready(function() {
    console.log('JS-файл загружен, данные:', window.portfolioData || portfolioData);
    console.log('Media URL:', window.mediaUrl);
    // Обработчик клика по карточке
    $('.portfolio-card').on('click', function() {
        const cardId = $(this).data('id'); // Получаем ID из data-атрибута
        const data = portfolioData[cardId];
        if (!data) {
            console.error('Данные для ID', houseId, 'не найдены');
            return;
        }
        if (data) {
            // Заполняем модальное окно данными
            $('#modalTitle').text(data.title);
            $('#modalDescription').text(data.description);
            $('#modalPrice').text(data.price);
            $('#modalArea').text(data.area);
            // Используем MEDIA_URL для формирования путей
        const imageUrl = window.mediaUrl + 'portfolio/gallery/' + data.main_image;
            // Очищаем и наполняем слайдер фотографиями
            const slider = $('#modalSlider');
            slider.empty(); // Удаляем старые фото
            data.images.forEach(imageSrc => {

                slider.append(`<div><img src="${imageSrc}" alt="${data.title}"></div>`);
            });

            // Показываем модальное окно
            $('.modal').fadeIn();

            // Инициализируем или обновляем слайдер (если используется OwlCarousel)
            if (slider.hasClass('owl-loaded')) {
                slider.trigger('destroy.owl.carousel'); // Уничтожаем старый экземпляр
                slider.removeClass('owl-carousel owl-loaded');
            }
            slider.addClass('owl-carousel'); // Добавляем класс заново
            slider.owlCarousel({
                items: 1,
                loop: true,
                margin: 10,
                nav: true,
                dots: true,
                smartSpeed: 400
            });
        }
    });

    // Закрытие модального окна при клике на крестик
    $('.close-button').on('click', function() {
        $('.modal').fadeOut();
    });

    // Закрытие при клике на затемненную область вокруг окна
    $(window).on('click', function(event) {
        if ($(event.target).hasClass('modal')) {
            $('.modal').fadeOut();
        }
    });
});