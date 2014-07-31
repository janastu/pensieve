var S = window.S || {};
(function(S, config) {

  var Result = Backbone.Model.extend({
    initialize: function(options) {
      this.set(options);
    }
  });

  var Results = Backbone.Collection.extend({
    model: Result,
    initialize: function() {
    }
  });

  var ResultsView = Backbone.View.extend({
    el: $("#search-container"),
    template: _.template($("#search-template").html()),
    initialize: function() {
      this.listenTo(this.collection, "reset", this.clearView);
      this.listenTo(this.collection, "add", this.render);
    },
    render: function(model) {
      model.set({"source_url":"//"+$("#input-site").val() + "/#" + model.get('_source')['name']});
      $(this.el).append(this.template(model.toJSON()));
    },
    clearView: function() {
      $(this.el).html('');
    }
  });

  var AppView = Backbone.View.extend({
    el:$("#app-container"),
    events: {
      "click #submitQuery": "submitQuery"
    },
    initialize: function() {
      // this.render();
    },
    submitQuery: function() {
      $(".alert").hide();
      var index = $("#input-site").val();
      var doc_type = $("#input-doc").val();

      $.get(config.searchEngine+index+"/"+doc_type+"/_search?",
            {q: $("#input-search").val()}, function(data) {
              if(S.results.length){
                S.results.reset();
              }
              if(data.hits.total) {
              S.results.add(data.hits.hits);
              }
              else {
                $(".alert").alert();
                $(".alert").show();
              }
            }).fail(function(data) {
              console.log("here");
              if(data.status == 404) {
                $(".alert").alert();
                $(".alert").show();
              }
            });
    }
  });
  new AppView;
  S.results = new Results();
  new ResultsView({collection: S.results});
})(S, config);
