<template>
    <v-container class="fill-height d-flex justify-center align-start">
      <v-card class="pa-6" max-width="900" elevation="4" width="100%">
        <v-card-title class="text-h6 font-weight-bold">
          📄 마크다운 보기
          <v-spacer />
          <v-btn
            color="primary"
            variant="tonal"
            :href="`http://localhost:8000/pdfs/${pdfId}/download`"
            target="_blank"
          >
            다운로드
          </v-btn>
        </v-card-title>
  
        <v-divider class="my-4" />
  
        <v-card-text>
          <div v-if="pageBlocks.length">
            <v-card
              v-for="(page, index) in pageBlocks"
              :key="index"
              class="mb-6 px-6 py-6"
              elevation="1"
            >
              <div v-html="page" class="page-content markdown-rendered" />
              <div class="text-right text-caption text-grey mt-6">Page {{ index + 1 }}</div>
            </v-card>
          </div>
          <v-alert v-else type="error" title="로드 실패" class="mt-4">
            마크다운을 불러올 수 없습니다.
          </v-alert>
        </v-card-text>
      </v-card>
    </v-container>
  </template>
  
  <script>
  import axios from 'axios'
  import { marked } from 'marked'
  
  marked.setOptions({
    gfm: true,
    breaks: true,
  })
  
  marked.use({
    renderer: {
      code(code) {
        return `<div class="markdown-code-block">${code}</div>`
      }
    }
  })
  
  export default {
    name: 'DetailView',
    data() {
      return {
        pageBlocks: [],
      }
    },
    computed: {
      pdfId() {
        return this.$route.params.pdf_id
      },
    },
    async mounted() {
      try {
        const res = await axios.get(`http://localhost:8000/pdfs/${this.pdfId}/markdown`)
        console.log('[✔] 응답 수신 완료:', res)
  
        if (res.status === 200 && res.data.success) {
          let raw = res.data.markdown
          console.log('[📦] 원본 마크다운 데이터 타입:', typeof raw)
          console.log('[📦] 원본 마크다운 샘플:', raw.slice(0, 500))
  
          if (typeof raw !== 'string') raw = String(raw)
  
          // 코드블럭 정리
          raw = raw.replace(/```[a-zA-Z]*\n?([\s\S]*?)```/g, (_, content) => content)
  
          // 페이지 구분 기준 --- 로 나눠 렌더링
          this.pageBlocks = raw.split(/\n?---+\n?/).map((page) => marked.parse(page.trim()))
  
          console.log('[✅] marked 파싱 완료')
        }
      } catch (err) {
        console.error('Markdown 렌더링 실패:', err)
      }
    }
  }
  </script>
  
  <style scoped>
  .markdown-rendered {
    font-family: 'Segoe UI', sans-serif;
    line-height: 1.8;
    white-space: pre-wrap;
    padding: 0.5em 0;
  }
  .markdown-rendered h1,
  .markdown-rendered h2,
  .markdown-rendered h3,
  .markdown-rendered h4,
  .markdown-rendered h5,
  .markdown-rendered h6 {
    margin-bottom: 1em;
  }
  .markdown-code-block {
    background: #f5f5f5;
    padding: 1em;
    border-radius: 4px;
    margin: 1em 0;
    font-family: 'Courier New', monospace;
    white-space: pre-wrap;
  }
  .page-content {
    overflow-wrap: break-word;
    word-break: break-word;
    padding-bottom: 0.5em;
  }
  </style>