(function($) {
  $(function() {
    var csrftoken = $('meta[name=csrf-token]').attr('content');
    $.ajaxPrefilter(function( options, originalOptions, jqXHR ) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(options.type)) {
        jqXHR.setRequestHeader("X-CSRFToken", csrftoken);
      }
    });
  });
})(window.jQuery)
