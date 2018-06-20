"use strict";
goog.provide('HelloWorld');
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
                    data: { 'param1': this.param1, 'param2': this.param2 },
                    success: function (data) {
                        $("#GETDiv").html('GET helloworld: ' + data['helloworld']);
                    },
                });
            };
            ClassTest.prototype.Post = function () {
                $.ajax({
                    type: "POST",
                    url: "/test/helloworld",
                    data: JSON.stringify({ 'param1': this.param1, 'param2': this.param2 }),
                    success: function (data) {
                        $("#POSTDiv").html('POST helloworld: ' + data['helloworld']);
                    },
                });
            };
            return ClassTest;
        }());
        HelloWorld.ClassTest = ClassTest;
        function Init() {
            var t = new test.HelloWorld.ClassTest(123, 432);
            $(document).ready(function () {
                $("#testGET").click(function () {
                    t.Get();
                });
                $("#testPOST").click(function () {
                    t.Post();
                });
            });
        }
        HelloWorld.Init = Init;
    })(HelloWorld = test.HelloWorld || (test.HelloWorld = {}));
})(test || (test = {}));
window['HelloWorld'] = test.HelloWorld.Init;
