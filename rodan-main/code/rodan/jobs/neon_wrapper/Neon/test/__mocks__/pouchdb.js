/*eslint-env jest*/

let PouchDB = require('pouchdb-core');
PouchDB.plugin(require('pouchdb-adapter-memory'));
PouchDB.preferredAdapters = PouchDB.preferredAdapters.reverse();
module.exports = { default: PouchDB };
