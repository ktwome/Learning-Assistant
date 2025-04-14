<template>
    <v-container>
      <v-card class="mx-auto" max-width="600">
        <v-card-title>PDF 파일 업로드</v-card-title>
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
          <v-spacer />
          <v-btn color="primary" :disabled="!pdfFile" @click="uploadFile">
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
      }
    },
    methods: {
      async uploadFile() {
        const formData = new FormData()
        formData.append('file', this.pdfFile)
  
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
        }
      },
    },
  }
  </script>
  