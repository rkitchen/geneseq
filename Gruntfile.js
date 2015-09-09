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
          "app/html/css/main.css": "app/html/less/main.less", // destination file and source file
          "app/html/css/graphics.css": "app/html/less/graphics.less"
        }
      }
    },
    watch: {
      styles: {
        files: ["app/html/less/*"], // which files to watch
        tasks: ['less'],
        options: {
          nospawn: true
        }
      }
    }
  });

  grunt.registerTask('default', ['less', 'watch']);
};
