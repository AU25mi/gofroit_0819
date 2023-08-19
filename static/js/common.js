function clearTextarea() {
    var textareaForm = document.getElementById("word");
    textareaForm.value = '';
}



$(function () { // ここはお約束
    // メニューを表示させる
    $('.hum_menu').on('click', function () {
        $('.word-container').toggleClass('open');
    });
    // マイナスをつけたい
    $('.hum_menu').on('click', function () {
        $('.hum_menu').toggleClass('active');
    });
});//JQueryのお約束。消しちゃダメ！