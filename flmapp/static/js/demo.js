let last_name,first_name,last_name_kana,first_name_kana,zip01,pref01,addr01,addr02,addr03,demo_btn;

window.onload = function () {
    last_name = document.getElementById("last_name");
    first_name = document.getElementById("first_name");
    last_name_kana = document.getElementById("last_name_kana");
    first_name_kana = document.getElementById("first_name_kana");
    zip01 = document.getElementById("zip01");
    pref01 = document.getElementById("pref01");
    addr01 = document.getElementById("addr01");
    addr02 = document.getElementById("addr02");
    addr03 = document.getElementById("addr03");
    demo_btn = document.getElementById("demo_btn");
}

function addDemo(){
    last_name.value = "山田";
    first_name.value = "花子";
    last_name_kana.value = "ヤマダ";
    first_name_kana.value = "ハナコ"
    zip01.value = "4500002";
    pref01.value = "愛知県";
    addr01.value = "名古屋市中村区名駅";
    addr02.value = "４丁目２７−１";
    addr03.value = "スパイラルタワーズ";
}