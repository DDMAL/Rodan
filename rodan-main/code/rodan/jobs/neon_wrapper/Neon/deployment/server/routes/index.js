/* eslint spaced-comment: ["error", "always", { "exceptions": ["/"] }] */
var express = require('express');
var fs = require('fs-extra');
var multer = require('multer');
const request = require('request');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

var router = express.Router();
const __base = '';

const manifestUpload = path.join(__base, 'deployment', 'public', 'uploads', 'manifests');
const meiUpload = path.join(__base, 'deployment', 'public', 'uploads', 'mei');
const imgUpload = path.join(__base, 'deployment', 'public', 'uploads', 'img');
const iiifUpload = path.join(__base, 'deployment', 'public', 'uploads', 'iiif');
const iiifPublicPath = path.join('/', 'uploads', 'iiif');
const neonContext = 'https://ddmal.music.mcgill.ca/Neon/contexts/1/manifest.jsonld';

const allowedPattern = /^[-_\.,\d\w ]+$/;
const consequtivePeriods = /\.{2,}/;

var upload = multer({
  storage: multer.memoryStorage(),
  limits: { filesize: 100000 }
});

function isUserInputValid (input) {
  return (input.match(allowedPattern) && !input.match(consequtivePeriods));
}

//////////////////
// Index routes //
//////////////////

// Main Page
router.route('/')
  .get(function (req, res) {
    var meiFiles = [];
    var iiifFiles = [];
    fs.readdir(manifestUpload, function (err, files) {
      if (err) {
        console.error(err);
        res.sendStatus(500);
        return;
      }
      if (files.length !== 0) {
        var index = files.indexOf('.gitignore');
        files.splice(index, (index < 0 ? 0 : 1));
        meiFiles = files;
      }

      fs.readdir(iiifUpload, { withFileTypes: true }, function (err, files) {
        if (err) {
          console.error(err);
          res.sendStatus(500);
          return;
        }
        files.filter(entry => { return entry.isDirectory(); }).forEach(entry => {
          let label = entry.name;
          let revisions = fs.readdirSync(path.join(iiifUpload, label), { withFileTypes: true });
          revisions.filter(entry => { return entry.isDirectory(); }).forEach(entry => {
            if (err) {
              console.error(err);
              res.sendStatus(500);
            } else {
              iiifFiles.push([label, entry.name]);
            }
          });
        });
        if (meiFiles.length !== 0 || iiifFiles.length !== 0) {
          res.render('index', { 'files': meiFiles, 'iiif': iiifFiles });
        } else {
          res.render('index', { 'nofiles': 'No files uploaded', 'files': meiFiles, 'iiif': iiifFiles });
        }
      });
    });
  });

router.route('/upload_file').post(upload.array('resource', 2), function (req, res) {
  // Check media type
  if (!req.files[1].mimetype.match(/^image\/*/)) {
    res.sendStatus(415); // Unsupported Media Type
  } else {
    let meiFileName = req.files[0].originalname;
    let basename = meiFileName.split(/\.mei$/, 2)[0];
    let imageExtension = /^.*(\.[a-zA-Z0-9]+)$/.exec(req.files[1].originalname)[1];
    let imageName = basename + (imageExtension !== null ? imageExtension : '');
    let manifestName = basename + '.jsonld';
    // Validate the file names
    if (!isUserInputValid(meiFileName) || !isUserInputValid(imageName) || !isUserInputValid(manifestName)) {
      res.sendStatus(403); // Forbidden
    } else {
      let manifest = {
        '@context': neonContext,
        '@id': '/uploads/manifests/' + manifestName,
        title: basename,
        timestamp: (new Date()).toISOString(),
        image: '/uploads/img/' + imageName,
        mei_annotations: [
          {
            id: 'urn:uuid:' + uuidv4(),
            type: 'Annotation',
            body: '/uploads/mei/' + meiFileName,
            target: '/uploads/img/' + imageName
          }
        ]
      };
      // Ensure files do not already exist
      if (fs.existsSync(path.join(meiUpload, meiFileName)) || fs.existsSync(path.join(imgUpload, imageName)) || fs.existsSync(path.join(manifestUpload, manifestName))) {
        res.sendStatus(409); // Conflict
      } else {
        // Write files
        try {
          fs.writeFileSync(path.join(meiUpload, meiFileName), req.files[0].buffer);
          fs.writeFileSync(path.join(imgUpload, imageName), req.files[1].buffer);
          fs.writeFileSync(path.join(manifestUpload, manifestName), JSON.stringify(manifest, null, 4));
        } catch (e) {
          console.error(e);
          res.sendStatus(500);
          return;
        }
        res.redirect('/');
      }
    }
  }
});

// Delete file TODO: Optimize function with regex
router.route('/delete/:filename')
  .get(function (req, res) {
    if (!isUserInputValid(req.params.filename)) {
      return res.sendStatus(403);
    }
    fs.readFile(path.join(manifestUpload, req.params.filename), (err, data) => {
      if (err) {
        console.error(err);
        res.sendStatus(404);
      } else {
        let manifest = JSON.parse(data);
        let imagePath = manifest.image.split('/');
        let meiPath = manifest.mei_annotations[0].body.split('/');
        try {
          fs.unlinkSync(path.join(manifestUpload, req.params.filename));
          fs.unlinkSync(path.join('deployment', 'public', ...imagePath));
          fs.unlinkSync(path.join('deployment', 'public', ...meiPath));
        } catch (e) {
          console.error(e);
          return res.sendStatus(500);
        }
        res.redirect('/');
      }
    });
  });

// Delete IIIF files
router.route('/delete/:label/:rev').get((req, res) => {
  if (!isUserInputValid(req.params.label) || !isUserInputValid(req.params.rev)) {
    res.sendStatus(403);
  }
  let somePath = path.join(iiifUpload, req.params.label, req.params.rev);
  fs.remove(somePath, (err) => {
    if (err) {
      console.error(err);
    }
    res.redirect('/');
  });
});

// redirect to editor
router.route('/edit/:filename').get(function (req, res) {
  if (!isUserInputValid(req.params.filename)) {
    return res.sendStatus(403);
  }

  // Check that the manifest exists
  fs.stat(path.join(manifestUpload, req.params.filename), (err, stats) => {
    if (err) {
      if (err.code !== 'ENOENT') {
        console.error(err);
      }
      res.sendStatus(404); // Not Found
    } else {
      // Read manifest
      fs.readFile(path.join(manifestUpload, req.params.filename), (err, data) => {
        if (err) {
          console.error(err);
          res.sendStatus(500); // Internal Server Error
        } else {
          res.render('editor', { 'manifest': encodeURIComponent(data) });
        }
      });
    }
  });
});

// redirect to salzinnes editor
router.route('/edit/:label/:rev').get((req, res) => {
  if (!isUserInputValid(req.params.label) || !isUserInputValid(req.params.rev)) {
    return res.sendStatus(403);
  }
  let pathName = path.join(req.params.label, req.params.rev);
  fs.readFile(path.join(iiifUpload, pathName, 'manifest.jsonld'), (err, data) => {
    if (err) {
      console.error(err);
      res.status(500).render('error', { statusCode: '500 - Internal Server Error', message: 'Could not find the manifest for IIIF entry ' + pathName });
    } else {
      res.render('editor', { 'manifest': encodeURIComponent(data) });
    }
  });
});

router.route('/add-iiif').get(function (req, res) {
  res.render('add-iiif', {});
}).post(function (req, res) {
  if (req.body.manifest === undefined || req.body.revision === undefined) {
    res.render('add-iiif', { messages: 'All fields are required!' });
  } else {
    request(req.body.manifest, (error, response, body) => {
      if (error) {
        res.render('add-iiif', { messages: error });
      } else if (!response.statusCode === 200) {
        res.render('add-iiif', { messages: 'Received status code ' + response.statusCode });
      } else {
        let manifest;
        try {
          manifest = JSON.parse(body);
        } catch (e) {
          res.render('add-iiif', { messages: 'URL was not to a valid JSON object.' });
        }
        if (manifest['@context'] !== 'http://iiif.io/api/presentation/2/context.json' ||
            manifest['@type'] !== 'sc:Manifest') {
          res.render('add-iiif', { messages: 'URL was not to a IIIF Presentation manifest.' });
        }

        // Check if a revision for this already exists.
        let label = manifest.label;
        if (label === undefined) {
          res.status(400).render('error', {
            statusCode: '400 - Bad Request',
            message: 'The provided manifest does not have a label and cannot be processed.'
          });
        }
        if (!isUserInputValid(label) || !isUserInputValid(req.body.revision)) {
          res.sendStatus(403);
        }
        let directoryExists = true;
        try {
          fs.accessSync(path.join(iiifUpload, label, req.body.revision));
        } catch (e) {
          directoryExists = false;
        }
        if (directoryExists) {
          res.render('add-iiif', { messages: 'The revision specified already exists!' });
          return;
        }

        // Create appropriate directory
        fs.mkdir(path.join(iiifUpload, label, req.body.revision), { recursive: true }, (err) => {
          if (err) {
            console.error(err);
            res.sendStatus(500);
          }
          let manifest = {
            '@context': neonContext,
            '@id': '/uploads/iiif/' + label + '/' + req.body.revision + '/manifest.jsonld',
            'title': label,
            'timestamp': (new Date()).toISOString(),
            'image': req.body.manifest,
            'mei_annotations': []
          };
          fs.writeFile(path.join(iiifUpload, label, req.body.revision, 'manifest.jsonld'),
            JSON.stringify(manifest, null, 4),
            (err) => {
              if (err) {
                console.error(err);
                res.sendStatus(500);
              }
              res.render('add-mei-iiif', { label: label, rev: req.body.revision });
            });
        });
      }
    });
  }
});

router.route('/add-mei-iiif/:label/:rev').post(upload.array('mei'), function (req, res) {
  if (!isUserInputValid(req.params.label) || !isUserInputValid(req.params.rev)) {
    res.sendStatus(403);
  }
  let manifest;
  try {
    manifest = JSON.parse(fs.readFileSync(path.join(iiifUpload, req.params.label, req.params.rev, 'manifest.jsonld')));
  } catch (e) {
    console.error(e);
    res.sendStatus(500);
  }

  request(manifest.image, (error, response, body) => {
    if (error) {
      res.send(error);
    } else if (!response.statusCode === 200) {
      res.status(response.statusCode).send(response.statusMessage);
    } else {
      let iiif;
      try {
        manifest = JSON.parse(body);
      } catch (e) {
        res.status(500).send('Could not parse the JSON object');
      }

      let labels = [];
      let ids = [];

      for (let sequence of manifest['sequences']) {
        for (let canvas of sequence['canvases']) {
          labels.push(canvas['label']);
          ids.push(canvas['@id']);
        }
      }

      // Check file names for conflicts
      for (let i = 0; i < req.files.length; i++) {
        for (let j = i + 1; j < req.files.length; j++) {
          if (req.files[i].originalname === req.files[j].originalname) {
            res.render('add-mei-iiif', { label: req.params.label, rev: req.params.rev, message: 'Two files with the name ' + req.files[i].originalname + ' were selected.' });
          }
        }
      }

      // Store files and create array of file names
      let filenames = [];
      for (let file of req.files) {
        fs.writeFileSync(path.join(iiifUpload, req.params.label,
          req.params.rev, file.originalname), file.buffer);
        filenames.push(file.originalname);
      }

      // res.status(501).render('error', { statusCode: '501 - Not Implemented', message: 'Adding a IIIF manifest and MEI files is not fully supported yet. Sorry!' });
      res.render('associate-mei-iiif',
        {
          label: req.params.label,
          rev: req.params.rev,
          files: filenames,
          labels: labels,
          ids: ids
        }
      );
    }
  });
});

router.route('/associate-mei-iiif/:label/:rev').post(function (req, res) {
  if (!isUserInputValid(req.params.label) || !isUserInputValid(req.params.rev)) {
    res.sendStatus(403);
  }
  // Load manifest file
  let manifest;
  try {
    manifest = JSON.parse(fs.readFileSync(path.join(iiifUpload, req.params.label, req.params.rev, 'manifest.jsonld')));
  } catch (e) {
    console.error(e);
    return res.sendStatus(500);
  }

  manifest.mei_annotations = [];
  if (typeof req.body.select !== 'string') {
    for (let entryText of req.body.select) {
      let entry = JSON.parse(entryText);
      manifest.mei_annotations.push({
        'id': 'urn:uuid:' + uuidv4(),
        'type': 'Annotation',
        'body': '/uploads/iiif/' + req.params.label + '/' + req.params.rev + '/' + entry.file,
        'target': entry.id
      });
    }
  } else {
    let entry = JSON.parse(req.body.select);
    manifest.mei_annotations.push({
      'id': 'urn:uuid:' + uuidv4(),
      'type': 'Annotation',
      'body': '/uploads/iiif/' + req.params.label + '/' + req.params.rev + '/' + entry.file,
      'target': entry.id
    });
  }

  fs.writeFile(path.join(iiifUpload, req.params.label, req.params.rev, 'manifest.jsonld'),
    JSON.stringify(manifest, null, 4), (err) => {
      if (err) {
        console.error(err);
        res.sendStatus(500);
      } else {
        res.redirect('/');
      }
    });
});

router.route('/uploads/mei/:file').put(function (req, res) {
  if (!isUserInputValid(req.params.file)) {
    res.sendStatus(403);
    return;
  }
  if (typeof req.body.mei === 'undefined') {
    res.sendStatus(400);
    return;
  }

  // Check if file file exists. If it does, write. Otherwise return 404
  let filePath = path.join(meiUpload, req.params.file);
  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (err) {
      res.sendStatus(404);
    } else {
      fs.writeFile(filePath, req.body.mei, (err) => {
        if (err) {
          console.error(err);
          res.sendStatus(500);
        } else {
          res.sendStatus(200);
        }
      });
    }
  });
});

router.route('/uploads/iiif/:label/:rev/:file').put(function (req, res) {
  if (!isUserInputValid(req.params.label) || !isUserInputValid(req.params.rev) || !isUserInputValid(req.params.file)) {
    res.sendStatus(403);
    return;
  }
  if (typeof req.body.mei === 'undefined') {
    res.sendStatus(400);
    return;
  }

  // Check if file exists. If it does, write. Otherwise 404.
  let filePath = path.join(iiifUpload, req.params.label, req.params.rev, req.params.file);
  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (err) {
      res.sendStatus(404);
    } else {
      fs.writeFile(filePath, req.body.mei, (err) => {
        if (err) {
          console.error(err);
          res.sendStatus(500);
        } else {
          res.sendStatus(200);
        }
      });
    }
  });
});

module.exports = router;
