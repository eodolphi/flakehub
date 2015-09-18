import Ember from 'ember';

export default Ember.Object.extend({
  open (authentication) {
    var authorizationCode = authentication.authorizationCode;

    return Ember.$.ajax({
        url: 'api/session',
        data: {code: authorizationCode },
        dataType: 'json',
    }).then(function(session) {
      localStorage.jwtToken = session.access_token;
      return session;
    });
  },
  fetch () {
    return Ember.$.ajax({
      url: 'api/user',
      dataType: 'json',
      headers: {Authorization: `Bearer ${localStorage.jwtToken}`}
    }).then(function (user) {
      user.access_token = localStorage.jwtToken;
      return user;
    });
  }
});
