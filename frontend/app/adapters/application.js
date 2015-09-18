import Ember from 'ember';
import DS from 'ember-data';

export default DS.RESTAdapter.extend({
  namespace: 'api',
  headers: Ember.computed('session.access_token', function () {

    var token = localStorage.jwtToken;
    return {Authorization: `Bearer ${token}`};
  })
});
