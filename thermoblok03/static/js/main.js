        $("#menu").on("click", ".ex", function (event) {
            event.preventDefault();
            var href = $(this).attr('href');
            var target = $(href);
            var top = target.offset().top;
            $('body,html').animate({ scrollTop: top }, 1000);
        });
        $('.q').on('click', function () {
            var objName = this.getAttribute('data-id');
            var obj = $(objName);
            $('.q').removeClass('on');
            if (obj.css("display") != "none") {
                obj.animate({
                    height: 'hide',
                }, 300);
            }
            else {
                var visibleBlocks = $("div[id*='menu-']:visible");
                if (visibleBlocks.length < 1) {
                    obj.animate({
                        height: 'show',
                    }, 300);
                    $(this).addClass('on');
                } else {
                    $(visibleBlocks).animate({
                        height: 'hide',
                    }, 300);
                }
            }
        });
        var icons = document.getElementsByClassName("main_icon");
        var icons_i = 0;
        var icon;
        var timerId = setInterval(function () {
            $(".main_icon").removeClass("active");
            icon = icons[icons_i];
            $(icon).addClass("active");
            icons_i++;
            if (icons_i == 3) {
                icons_i = 0;
            }
        }, 2000);
        $(document).ready(function () {
            $(function () {
                if (location.hash.length) {
                    var target = $('[name="' + location.hash.substr(1) + '"]');
                    if (!target.length)
                        target = $(location.hash);
                    if (target.length)
                        $('html,body').animate({ scrollTop: target.offset().top }, 1000);
                };
            });
            $('.main_slider').on('init', function (e, slick) {
                var $firstAnimatingElements = $('div.item:first-child').find('[data-animation]');
                doAnimations($firstAnimatingElements);
            });
            $('.main_slider').on('beforeChange', function (e, slick, currentSlide, nextSlide) {
                var $animatingElements = $('div.item[data-slick-index="' + nextSlide + '"]').find('[data-animation]');
                doAnimations($animatingElements);
            });
            $('.main_slider').slick({
                infinite: true,
                autoplay: true,
                autoplaySpeed: 4000,
                dots: true,
                arrows: true,
                speed: 500,
                fade: true,
                cssEase: 'linear',
            });
            $('.nav_slider').slick({
                arrows: true,
                variableWidth: true,
                infinite: false,
            });
            $('.articles_slider').slick({
                arrows: true,
                dots: false,
                infinite: true,
                slidesToShow: 3,
                slidesToScroll: 2,
                responsive: [
                    {
                        breakpoint: 991,
                        settings: {
                            slidesToShow: 2,
                            slidesToScroll: 2,
                        }
                    },
                    {
                        breakpoint: 600,
                        settings: {
                            slidesToShow: 1,
                            slidesToScroll: 1
                        }
                    }]
            });
            $('.achievements_slider').slick({
                arrows: true,
                dots: false,
                infinite: true,
                slidesToShow: 6,
                slidesToScroll: 3,
                responsive: [
                    {
                        breakpoint: 991,
                        settings: {
                            slidesToShow: 3,
                            slidesToScroll: 2,
                        }
                    },
                    {
                        breakpoint: 575,
                        settings: {
                            slidesToShow: 1,
                            slidesToScroll: 1
                        }
                    }]
            });
            $('.articles_list_slider').slick({
                arrows: true,
                dots: false,
                infinite: true,
                slidesToShow: 3,
                slidesToScroll: 2,
                responsive: [
                    {
                        breakpoint: 991,
                        settings: {
                            slidesToShow: 2,
                            slidesToScroll: 2,
                        }
                    },
                    {
                        breakpoint: 600,
                        settings: {
                            slidesToShow: 1,
                            slidesToScroll: 1
                        }
                    }]
            });
            function doAnimations(elements) {
                var animationEndEvents = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
                elements.each(function () {
                    var $this = $(this);
                    var $animationDelay = $this.data('delay');
                    var $animationType = 'animated ' + $this.data('animation');
                    $this.css({
                        'animation-delay': $animationDelay,
                        '-webkit-animation-delay': $animationDelay,
                        'opacity': 1
                    });
                    $this.addClass($animationType).one(animationEndEvents, function () {
                        $this.removeClass($animationType);
                    });
                });
            };
            $(".floating").on('click', function () {
                var animationEndEvents = 'webkitAnimationEnd animationend';
                var elem = $(".floating_icons_wrapper");
                elem.removeClass("fadeInUp animated");
                if (elem.hasClass("d-none")) {
                    $(".floating").addClass("active");
                    elem.removeClass("d-none").addClass("fadeInUp animated");
                }
                else {
                    elem.addClass("d-none");
                    $(".floating").removeClass("active");
                }
            });
        });