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

export default {
  name: 'ResultView',
  data() {
    return {
      markdownHtml: '',
    }
  },
  mounted() {
    try {
      const rawMarkdown = localStorage.getItem('markdown')
      if (rawMarkdown) {
        this.markdownHtml = marked.parse(rawMarkdown)
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
  line-height: 1.7;
  white-space: pre-wrap;
}
</style>
