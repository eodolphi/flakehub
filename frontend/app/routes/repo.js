import Ember from 'ember';

export default Ember.Route.extend({
  model(params) {
    var store = this.get('store');
    var path = `${params.owner}/${params.name}`;

    return Ember.RSVP.hash({
     repo: store.find('repo', path),
      hook: store.find('hook', path)
    });
  },
  actions: {
    toggle (hook) {
      hook.set('active', !hook.get('active'));

      hook.save().then(function () {
        hook.reload();
      });
    }
  }

});
