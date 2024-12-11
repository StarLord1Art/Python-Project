(function (DateFormatter) {
    /**
      * dvxCharts Dutch Translation
      * http://www.dvxcharts.com/
      * 
      * In order to use a particular language pack, you need to include the JavaScript language
      * pack to the head of your page, after referencing the dvxCharts.chart JavaScript file.
      * 
      * <script src="../js/dvxCharts.chart.min.js" type="text/javascript"></script>
      * <script src="../js/i18n/chart.locale-xx.js" type="text/javascript"></script>
      **/
    DateFormatter.DateFormat = {
        dayNames: [
            "Zo", "Ma", "Di", "Wo", "Do", "Vr", "Za",
            "Zondag", "Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag"
        ],
        monthNames: [
            "Jan", "Feb", "Maa", "Apr", "Mei", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
            "Januari", "Februari", "Maart", "April", "Mei", "Juni", "Juli", "Augustus", "September", "October", "November", "December"
        ],
        amPm: ["am", "pm", "AM", "PM"],
        s: function (b) {
            return b < 11 || b > 13 ? ["st", "nd", "rd", "th"][Math.min((b - 1) % 10, 3)] : "th"
        },
        masks: {
            shortDate: "m/d/yyyy",
            shortTime: "H:MM",
            longTime: "H:MM:ss"
        }
    };
})(dvxCharts.DateFormatter);