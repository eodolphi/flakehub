import Ember from 'ember';
import DS from 'ember-data';

var inflector = Ember.Inflector.inflector;

inflector.uncountable('user');

export default DS.Model.extend({
});

