module.exports = function(grunt) {
  require('jit-grunt')(grunt);

  grunt.initConfig({
    jsdox: {
      generate: {
        src: ['source/app/html/js/dev/*'],
        dest: 'docs/api/'
      }
    },
    less: {
      development: {
        options: {
          compress: true,
          yuicompress: true,
          optimization: 2
        },
        files: {
          "source/app/html/css/main.css": "source/app/html/less/main.less", // destination file and source file
          "source/app/html/css/graphics.css": "source/app/html/less/graphics.less",
          "source/app/html/css/login.css": "source/app/html/less/login.less"
        }
      }
    },
    watch: {
      styles: {
        files: ["source/app/html/less/*"], // which files to watch
        tasks: ['less']
      },
      javascript: {
        files: ['source/app/html/js/dev/*'],
        tasks: ['jsdox']
      }
    }
  });

  grunt.loadNpmTasks('grunt-jsdox');
  grunt.registerTask('default', ['jsdox', 'less', 'watch']);
};
