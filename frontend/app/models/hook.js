import DS from 'ember-data';

export default DS.Model.extend({
  hook_url: DS.attr('string'),
  active: DS.attr('boolean')

});
