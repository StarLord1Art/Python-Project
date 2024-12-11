(function (DateFormatter) {
    /**
      * dvxCharts Norwegian Translation
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
            "sø.", "ma.", "ti.", "on.", "to.", "fr.", "lø.",
            "Søndag", "Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag"
        ],
        monthNames: [
            "jan.", "feb.", "mars", "april", "mai", "juni", "juli", "aug.", "sep.", "okt.", "nov.", "des.",
            "januar", "februar", "mars", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "desember"
        ],
        amPm: ["", "", "", ""],
        s: function (b) { return "." },
        masks: {
            shortDate: "d.m.yyyy",
            shortTime: "HH:MM",
            longTime: "HH:MM:ss"
        }
    };
})(dvxCharts.DateFormatter);
