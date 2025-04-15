<template>
  <!-- 로딩 오버레이 -->
  <v-overlay :model-value="loading" persistent class="d-flex justify-center align-center">
    <v-card color="white" class="pa-4 text-center" elevation="2">
      <v-progress-circular indeterminate size="48" color="primary" class="mb-4" />
      <div>문서를 처리 중입니다. 잠시만 기다려 주세요...</div>
    </v-card>
  </v-overlay>

  <!-- 업로드 카드 -->
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card class="pa-6" max-width="600" elevation="4">
      <v-card-title class="text-h6 font-weight-bold mb-2">
        📄 PDF → Markdown 변환
      </v-card-title>

      <v-card-text class="mb-4">
        PDF 강의자료를 업로드하면 구조화된 Markdown으로 자동 변환됩니다.
      </v-card-text>

      <v-file-input
        v-model="pdfFile"
        label="PDF 파일 선택"
        accept=".pdf"
        show-size
        outlined
        clearable
        class="mb-4"
      />

      <v-card-actions class="d-flex justify-space-between">
        <v-btn color="grey-darken-1" variant="tonal" to="/" :disabled="loading">
          ← 홈으로
        </v-btn>
        <v-btn color="primary" :disabled="!pdfFile || loading" @click="uploadFile">
          업로드
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  name: 'UploadView',
  data() {
    return {
      pdfFile: null,
      loading: false,
    }
  },
  methods: {
    async uploadFile() {
      if (!this.pdfFile) return
      const formData = new FormData()
      formData.append('file', this.pdfFile)
      this.loading = true

      try {
        const res = await axios.post('http://localhost:8000/pdfs', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })

        if (res.status === 200 && res.data.success) {
          const pdfId = res.data.id
          this.$router.push(`/view/${pdfId}`)
        } else {
          throw new Error('서버 응답 오류')
        }
      } catch (err) {
        console.error('업로드 실패:', err)
        alert('파일 업로드에 실패했습니다.')
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.fill-height {
  min-height: calc(100vh - 64px);
}
</style>
