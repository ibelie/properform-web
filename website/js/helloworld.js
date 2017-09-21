goog.provide('test.HelloWorld.ClassTest');
var test;
(function (test) {
    var HelloWorld;
    (function (HelloWorld) {
        var ClassTest = (function () {
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
                        $("#GETDiv").html('Get helloworld: ' + data.helloworld);
                    }
                });
            };
            ClassTest.prototype.Post = function () {
                var result = $.ajax({
                    type: "POST",
                    url: "/test/helloworld",
                    data: { param1: this.param1, param2: this.param2 },
                    success: function (data) {
                        $("#POSTDiv").html('Get helloworld: ' + data.helloworld);
                    }
                });
            };
            return ClassTest;
        }());
        HelloWorld.ClassTest = ClassTest;
    })(HelloWorld = test.HelloWorld || (test.HelloWorld = {}));
})(test || (test = {}));
