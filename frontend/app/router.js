import Ember from 'ember';
import config from './config/environment';

var Router = Ember.Router.extend({
  location: config.locationType
});

Router.map(function() {
  this.route('repo-list');
  this.route('repo', {path: 'repo/:owner/:name'});
});

export default Router;
