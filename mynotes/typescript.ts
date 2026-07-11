// npm install typescrit -g
// tsc --init 生成tsconfig.json文件 "target": "ES6"
// tsconfig.json 中添加 "include": ["pathTSFile"] 执行 tsc 自动按照配置文件编译
// 或者删除tsconfig.json文件,使用 tsc 指定ts文件 编译 tsc --watch 会自动监视编译
// 使用 : 类型声明 
let type: any = "any type" // 不进行类型声明即隐式any 可以任意赋值,破坏其他声明
const unknownNow: unknown = "unknown type"
// 使用断言 
type = unknownNow as any 
(unknownNow as any).xxx 

function neverOver(): never {
  throw new Error("never")
}

// void 可以接受 return undefined
function voidReturn(): void {
  console.log(new Error("never"))
}

// object(对象类型) 与 Object(除null/undefined外)
// variableData? 字面量类型常用 表示有何不有都可 
let func: (arg: number) => number
func = function (arg) { return arg }

let arr1: number[]
let arr2: Array<number>

// 固定数量/类型且支持可选? 元组类型 
let tuple: [number, string, boolean?]
let moreTuple: [number, ...string[]]

// 一组一组相关值放到枚举,更快、防止写错
// 默认为数字枚举且从零开始(有方向映射)、字符串枚举(自定义值为字符串,没有反向映射) 
enum Color { Red, Green, Blue }
Color[0] // Red

// 别名与联合
type Name = string | number 

// 交叉 
type Address = {
  num: number,
  cell: number,
  room: string
}

type Area = {
  height: number,
  width: number 
}

type House = Address & Area 

class People {
  constructor(protected name: string) {
    this.name = name 
  }

  public sayHello() {
    console.log('hello')
  }
}

class Student extends People {
  constructor(protected name: string,
    public grade: string, private readonly idCard: string) {
    super(name)
    this.grade = grade 
    this.idCard = idCard 
  }

  public override sayHello() {
    console.log(`Hello, my name is ${this.name} and I'm in grade ${this.grade}`)
  }
}

// public 修饰符 类外部、内部、子类都能够使用 可以省略不写
// protected 修饰符 类内部和子类能够使用
// private 修饰符 只有类内部能够使用
// readonly 修饰符 设置只读属性

abstract class Abs {
  constructor(public name: string) { this.name = name }
  abstract sayHello(): void
  abs(): void {
    console.log('abs')
  }
}

class C extends Abs {
  constructor(public name: string) {
    super(name)
  }
  sayHello() {
    console.log('hello')
  }
}

// interface 有和并性与继承性 使用 implements 实现 多接口
// <> 泛型 定义时 使用时
// .d.ts文件 为现有的js代码提供类型信息 使得ts使用这些库或模块时也能类型检查和提示 
// .d.ts文件 可以从官方库中找 
