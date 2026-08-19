import * as Three from 'Three'
import { OrbitControls } from 'Three/addons/controls/OrbitControls.js'
import { GLTFLoader } from 'Three/addons/loaders/GLTFLoader.js'

let mixer, currentAction 
function setupAnimation(gltf) {
  const model = gltf.scene 
  const animations = gltf.animations 

  if (!annimations || animations.length === 0) {
    console.warn("该模型不包含任何动画")
    return 
  }

  mixer = new Three.AnimationMixer(model)
  const clip = animations[0] // 获取第一个动画剪辑并播放
  // animation.find(anim => anim.name === "animation_name") 通过名字查找 
  currentAction = mixer.clipAction(clip)
  currentAction.play() // 播放动画
  currentAction.setloop(Three.loopRepeat, Infinity) // 循环播放
  window.switchAnimation = function (index) {
    if (!animations[index]) return 
    if (currentAction) {
      currentAction.stop()
    }

    currentAction = mixer.clipAction(animations[index])
    currentAction.play()
  }
}

function setupUVControl(gltf) {
  // 创建纹理加载器
  const textureLoader = new Three.TextureLoader()
  const newTexture = textureLoader.load("path/to/your/texture.jpg") // 加载要替换的纹理图片

  gltf.scene.traverse((child) => {
    if (child.isMesh) {
      const materials = Array.isArray(child.material) ? child.material : [child.material]
      meterials.forEach((material) => {
        if (material.map) {
          material.map = newTexture 
          material.needsUpdate = true 
        }
      })
    }
  })
}

// --- 初始化场景、相机、渲染器 ---
const scene = new Three.Scene()
scene.background = new Three.Color(0x333333)

const camera = new Three.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000) // 视场角 宽高比 近裁剪面 远裁剪面 
camera.position.set(2, 1, 3) // x y z 坐标

const renderer = new Three.WebGLRenderer({ antialias: true }) // 抗锯齿
renderer.setSize(window.innerWidth, window.innerHeight) // 设置渲染画布尺寸
renderer.shadowMap.enabled = true // 开启阴影渲染 
document.body.appendChild(renderer.domElement) // 把画布插入页面

// --- 鼠标轨道控制器 ---
const controls = new OrbitControls(camera, renderer.domElement)
controls.target.set(0, 1, 0) // 控制器注视点
controls.update() // 初始化控制器参数

// --- 灯光 ---
const ambientLight = new Three.AmbientLight(0xcccccc)
scene.add(ambientLight)
const dirLight = new Three.DirectionalLight(0xffffff, 2) // 第二个参数表示灯光强度
dirLight.position.set(2, 5, 3)
dirLight.castShadow = true // 开启阴影投射
scene.add(dirLight)

// --- 加载模型 ---
const loader = new GLTFLoader()
loader.load('path/to/your/model.glb',
  (gltf) => {
    console.log('模型加载成功', gltf)
    const model = gltf.scene
    scene.add(model)

    // --- 接下来会在这里添加控制逻辑 ---
    setupAnimation(gltf)
    setupUVControl(gltf)
  },
  (xhr) => {
    console.log(`加载进度: ${(xhr.loaded / xhr.total) * 100}%`)
  },
  (error) => {
    console.error('模型加载失败:', error)
  }
)

// --- 渲染循环 ---
function animate() {
  requestAnimationFrame(animate)
  // 动画更新会在这里添加
  controls.update()
  renderer.render(scene, camera)
}
animate()



