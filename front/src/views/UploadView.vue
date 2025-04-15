<template>
  <!-- 로딩 오버레이 -->
  <v-overlay :model-value="loading" persistent class="d-flex justify-center align-center">
    <v-card color="white" class="pa-4 text-center" elevation="2">
      <v-progress-circular indeterminate size="48" color="primary" class="mb-4" />
      <div>문서를 처리 중입니다. 잠시만 기다려 주세요...</div>
    </v-card>
  </v-overlay>

  <!-- 업로드 카드 -->
  <v-container>
    <v-card class="mx-auto" max-width="600">
      <v-card-title class="text-h6">📄 마크다운 변환 페이지</v-card-title>

      <v-card-text>
        <v-file-input
          v-model="pdfFile"
          label="PDF 파일 선택"
          accept=".pdf"
          show-size
          outlined
        />
      </v-card-text>

      <v-card-actions>
        <v-btn color="error" variant="tonal" to="/">
          홈으로
        </v-btn>
        <v-spacer />
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
      const formData = new FormData()
      formData.append('file', this.pdfFile)
      this.loading = true

      try {
        const res = await axios.post('http://localhost:8000/preprocess-pdf', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })

        if (res.status === 200 && res.data.success) {
          localStorage.setItem('markdown', res.data.markdown)
          this.$router.push({ path: '/result' })
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
