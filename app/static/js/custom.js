$('.navbar-form .btn').click(function(e){
  e.preventDefault();
  var url   = '/search/';
  var query = $('.form-control').val();
  if(url.length > 0 && query.length > 0){
    document.location = url + query;
  }
});

(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),m=s.getElementsByTagName(o)[0];a.async=0;a.src=g;m.parentNode.insertBefore(a,m)})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
ga('create', 'UA-50821313-1', 't0rrents.herokuapp.com');
ga('send', 'pageview');