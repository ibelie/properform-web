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
                console.info('test.Get', this.param1, this.param2);
            };
            ClassTest.prototype.Post = function () {
                console.info('test.Post', this.param1, this.param2);
            };
            return ClassTest;
        }());
        HelloWorld.ClassTest = ClassTest;
    })(HelloWorld = test.HelloWorld || (test.HelloWorld = {}));
})(test || (test = {}));
