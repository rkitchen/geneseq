module.exports = function(grunt) {
  require('jit-grunt')(grunt);

  grunt.initConfig({
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
        tasks: ['less'],
        options: {
          nospawn: true
        }
      }
    }
  });

  grunt.registerTask('default', ['less', 'watch']);
};
