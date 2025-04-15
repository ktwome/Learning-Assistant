<template>
  <v-container>
    <v-card class="pa-4" max-width="900" elevation="2">
      <v-card-title>📄 분석된 마크다운</v-card-title>
      <v-card-text>
        <div v-if="markdownHtml" v-html="markdownHtml" class="markdown-rendered" />
        <div v-else>
          <v-alert type="warning" class="mt-4">
            결과 데이터를 불러오지 못했습니다.
          </v-alert>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import { marked } from 'marked'

// marked 설정 (코드블럭을 일반 div로 처리)
marked.use({
  renderer: {
    code(code) {
      return `<div class="markdown-code-block">${code}</div>`
    }
  }
})

export default {
  name: 'ResultView',
  data() {
    return {
      markdownHtml: '',
    }
  },
  mounted() {
  try {
    let raw = localStorage.getItem('markdown')

    // 코드 블럭 제거 (옵션)
    raw = raw.replace(/```[a-zA-Z]*\n?([\s\S]*?)```/g, (_, content) => content)

    marked.use({
      renderer: {
        code(code) {
          return `<div class="markdown-code-block">${code}</div>`
        }
      }
    })

    this.markdownHtml = marked.parse(raw)
  } catch (err) {
    console.error('Markdown 렌더링 실패:', err)
  }
}

}
</script>


<style scoped>
  .markdown-rendered {
    font-family: 'Segoe UI', sans-serif;
    line-height: 1.7;
    white-space: pre-wrap;
  }
  .markdown-code-block {
    background: #f5f5f5;
    padding: 1em;
    border-radius: 4px;
    margin: 1em 0;
    font-family: 'Courier New', monospace;
    white-space: pre-wrap;
  }
</style>
