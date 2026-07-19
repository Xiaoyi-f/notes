npm install md-editor-v3 

<MdEditor v-model="text :theme="light / dark"></MdEditor>

import { ref } from "vue"
import MdEditor from "md-editor-v3"
import "md-editor-v3/lib/style.css"

const text = ref("Hello MdEditor!")

// 工具栏定义
const toolBars = [
  'bold',          // 加粗
  'underline',     // 下划线
  'italic',        // 斜体
  'strikeThrough', // 删除线
  'title',         // 标题
  'sub',           // 下标
  'sup',           // 上标
  'quote',         // 引用
  'unorderedList', // 无序列表
  'orderedList',   // 有序列表
  'task',          // 任务列表
  'codeRow',       // 行内代码
  'code',          // 代码块
  'link',          // 链接
  'image',         // 图片
  'table',         // 表格
  'mermaid',       // Mermaid图表
  'katex',         // 数学公式
  'revoke',        // 撤销
  'next',          // 重做
  'save',          // 保存
  '=',             // 等宽
  'pageFullscreen',// 页面全屏
  'fullscreen',    // 全屏
  'preview',       // 预览
  'htmlPreview',   // HTML预览
  'catalog',       // 目录
  '-',             // 分隔符
  "myTool"         // 自定义工具
]

// 预览功能
<template>
	<!-- 文章预览 -->
  <MdPreview :id="id" :modelValue="text" />
  <!-- 目录预览 -->
  <MdCatalog :editorId="id" :scrollElement="scrollElement" />
</template>

<script setup>
import { ref } from 'vue';
import { MdPreview, MdCatalog } from 'md-editor-v3';
import 'md-editor-v3/lib/preview.css';

const id = 'preview-only';
const text = ref('# Hello Editor');
const scrollElement = document.documentElement;
</script>

// 上传图片 
const onUploadImg = async (files, callback) => {
  const res = await Promise.all(
    files.map((file) => {
      return new Promise((resolve, reject) => {
        const form = new FormData()
        form.append("file", file)

        axios.post("/api/img/upload", form, {
          headers: {
            "Content-Type": "multipart/form-data"
          }
        })
        .then((res) => resolve(res))
        .catch((err) => reject(err))
      })
    })
  )
  callback(res.map((item) => item.data.url))
}

// 获取目录
<template>
  <MdEditor v-model="text" @onGetCatalog="onGetCatalog" />
</template>

<script setup>
import { reactive } from 'vue'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

const state = reactive({
  text: '',
  catalogList: [],
})

const onGetCatalog = (list) => {
  state.catalogList = list
}
</script>

// 展示
<template>
  <MdPreview :modelValue="state.text" :id="state.id" :theme="state.theme" />
  <MdCatalog :editorId="state.id" :scrollElement="scrollElement" :theme="state.theme" />
</template>

<script setup>
import { reactive } from 'vue';
import { MdPreview, MdCatalog } from 'md-editor-v3';
import 'md-editor-v3/lib/preview.css';

const state = reactive({
  theme: 'dark',
  text: '',
  id: 'my-editor',
});

const scrollElement = document.documentElement;
</script>


