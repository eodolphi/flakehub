import Ember from 'ember';

export default Ember.Component.extend({
  actions: {
    authorize: function () {
      this.get('session').open('github-oauth2');
    }
  }
});
