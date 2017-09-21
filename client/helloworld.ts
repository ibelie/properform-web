declare var $;
declare var goog;

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
			$('sdf');
			console.info('test.Get', this.param1, this.param2);
		}

		public Post(): void {
			console.info('test.Post', this.param1, this.param2);
		}
	}
}
