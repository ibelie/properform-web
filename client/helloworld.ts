/// <reference path="../closure/closure.d.ts" />
/// <reference path="lib/jquery/jquery.d.ts" />

goog.require('jquery');

goog.provide('test.HelloWorld.ClassTest');

module test.HelloWorld {
	export class ClassTest {
		public param1: number;
		public param2: number;

		public constructor(param1: number, param2: number) {
			this.param1 = param1;
			this.param2 = param2;
		}

		public Get(): void {
			$.ajax({
				type: "GET",
				url: "/test/helloworld",
				data: {param1: this.param1, param2: this.param2},
				success : function(data) {
					$("#GETDiv").html('GET helloworld: ' + data.helloworld);
				},
			});
		}

		public Post(): void {
			var result = $.ajax({
				type: "POST",
				url: "/test/helloworld",
				data: JSON.stringify({param1: this.param1, param2: this.param2}),
				success : function(data) {
					$("#POSTDiv").html('POST helloworld: ' + data.helloworld);
				},
			});
		}
	}
}
