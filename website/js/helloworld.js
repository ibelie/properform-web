/// <reference path="../closure/closure.d.ts" />
/// <reference path="lib/jquery/jquery.d.ts" />
goog.require('jquery');
goog.provide('test.HelloWorld.ClassTest');
var test;
(function (test) {
    var HelloWorld;
    (function (HelloWorld) {
        var ClassTest = /** @class */ (function () {
            function ClassTest(param1, param2) {
                this.param1 = param1;
                this.param2 = param2;
            }
            ClassTest.prototype.Get = function () {
                $.ajax({
                    type: "GET",
                    url: "/test/helloworld",
                    data: { param1: this.param1, param2: this.param2 },
                    success: function (data) {
                        $("#GETDiv").html('GET helloworld: ' + data.helloworld);
                    },
                });
            };
            ClassTest.prototype.Post = function () {
                var result = $.ajax({
                    type: "POST",
                    url: "/test/helloworld",
                    data: { param1: this.param1, param2: this.param2 },
                    success: function (data) {
                        $("#POSTDiv").html('POST helloworld: ' + data.helloworld);
                    },
                });
            };
            return ClassTest;
        }());
        HelloWorld.ClassTest = ClassTest;
    })(HelloWorld = test.HelloWorld || (test.HelloWorld = {}));
})(test || (test = {}));
