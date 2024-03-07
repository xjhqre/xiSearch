const body = document.querySelector('body')
const sidebar = body.querySelector('.sidebar')
const toggle = body.querySelector('.toggle')
const showImgList = body.querySelector('.show-img-list')
const page1 = body.querySelector('.page1')
const page2 = body.querySelector('.page2')
const page3 = body.querySelector('.page3')
const extractLog = body.querySelector('.extract-log') // 提取日志div
const imageSearch = body.querySelector('#image-search')
const featureExtraction = body.querySelector('#feature-extraction') // 侧边栏提取特征按钮
const imgFolderPath = body.querySelector('#imgFolderPath') // 图片库地址输入框
const searchImagePath = body.querySelector('#searchImagePath') // 搜索图片路径输入框
const setting = body.querySelector('#setting') // 设置按钮
const searchImageButton = body.querySelector('#searchImageButton') // 搜索图片按钮
const featureFileStorageAddress = body.querySelector('#featureFileStorageAddress') // 特征文件存储地址输入框
const searchSimilarImagesNumber = body.querySelector('#searchSimilarImagesNumber') // 搜索相似图片数量输入框
let featureExtractionTimer = 1// 特征提取定时器
const message = new Message() // 气泡提示消息
let autoScroll = true;

// 侧边栏伸缩按钮点击事件
toggle.addEventListener('click', () => {
    sidebar.classList.toggle('close')
})

// 侧边栏图片搜索点击事件
imageSearch.addEventListener('click', () => {
    if (page1.classList.contains('hidden-page')) {
        page1.classList.remove('hidden-page')
    }
    if (!page2.classList.contains('hidden-page')) {
        page2.classList.add('hidden-page')
    }
    if (!page3.classList.contains('hidden-page')) {
        page3.classList.add('hidden-page')
    }
})

// 侧边栏特征提取点击事件
featureExtraction.addEventListener('click', () => {
    if (page2.classList.contains('hidden-page')) {
        page2.classList.remove('hidden-page')
    }
    if (!page1.classList.contains('hidden-page')) {
        page1.classList.add('hidden-page')
    }
    if (!page3.classList.contains('hidden-page')) {
        page3.classList.add('hidden-page')
    }
})

// 设置按钮点击事件
setting.addEventListener('click', () => {
    if (page3.classList.contains('hidden-page')) {
        page3.classList.remove('hidden-page')
    }
    if (!page1.classList.contains('hidden-page')) {
        page1.classList.add('hidden-page')
    }
    if (!page2.classList.contains('hidden-page')) {
        page2.classList.add('hidden-page')
    }
})

// 监听特征向量地址输入框变化
function featureFileStorageAddressChange() {
    window.pywebview.api.update_feature_path(featureFileStorageAddress.value).then(() => {
        // TODO 气泡提示
        console.log("更新特征文件存储地址成功")
    })
}

// 监听搜索相似图片数量变化
function searchSimilarImagesNumberChange() {
    window.pywebview.api.update_result_count(searchSimilarImagesNumber.value).then(() => {
        // TODO 气泡提示
        console.log("更新搜索相似图片数量成功")
    })
}

// 监听图片库地址变化
function imgFolderPathChange() {
    window.pywebview.api.update_gallery_path(imgFolderPath.value).then(() => {
        // TODO 气泡提示
        console.log("更新图片库地址成功")
    })
}

// 提取图片特征
function extractFeatures() {
    // 清空日志
    while (extractLog.firstChild) {
        extractLog.removeChild(extractLog.firstChild);
    }
    let line = document.createElement('div');
    line.textContent = '开始提取！';
    extractLog.appendChild(line);

    // 每隔1秒获取提取特征日志
    featureExtractionTimer = setInterval(getExtractionLog, 1000);
    window.pywebview.api.feature_extraction(imgFolderPath.value).then(() => {
        clearInterval(featureExtractionTimer)
        getExtractionLog()
    })

}

// 获取提取日志
function getExtractionLog() {
    window.pywebview.api.get_extraction_log().then((response) => {
        if (response.finish === 0) {
            let line = document.createElement('div');
            line.textContent = `已提取图片数量：${response.cnt} , 耗时：${response.time} 秒`;
            extractLog.appendChild(line);
        } else {
            let line = document.createElement('div');
            line.textContent = `提取完成！，共提取图片数量：${response.cnt} , 总耗时：${response.time} 秒`;
            extractLog.appendChild(line);
            if (response.error_img_path.length > 0) {
                let line2 = document.createElement('div');
                line2.textContent = `提取错误图片路径：`;
                extractLog.appendChild(line2);
                response.error_img_path.forEach(item => {
                    let line3 = document.createElement('div');
                    line3.textContent = item
                    extractLog.appendChild(line3);
                })
            }


        }
        if (autoScroll) {
            extractLog.scrollTop = extractLog.scrollHeight; // 滚动到底部
        }
    })
}

// 监听滚动事件
extractLog.addEventListener('scroll', function (event) {
    let element = event.target;
    // 如果滚动条位置不在底部，则停止自动滚动
    if (element.scrollHeight - element.scrollTop !== element.clientHeight) {
        autoScroll = false;
    } else {
        autoScroll = true;
    }
});

// 搜索图片
function searchImages() {
    if (searchImagePath.value === undefined || searchImagePath.value === "") {
        return
    }
    searchImageButton.classList.add('loading')
    // 清空之前查询的图片
    while (showImgList.firstChild) {
        showImgList.firstChild.remove();
    }
    window.pywebview.api.search_images(searchImagePath.value).then(loadImg)
}

// 加载图片
function loadImg(response) {
    for (let i = 0; i < response.img_path_list.length; i++) {
        const cell = document.createElement('div')
        cell.classList.add('cell')
        cell.innerHTML = `
		    <img src=${response.base64_list[i]} title=${response.img_path_list[i]} onclick="copyTextToClipboard(this)" />
		`
        showImgList.appendChild(cell)
    }
    message.setOption({
        message: '搜索完成！',
        type: "success",
        duration: 1000,
    });
    // 停止加载动画
    searchImageButton.classList.remove('loading')
}

// 复制图片地址
function copyTextToClipboard(imgDom) {
    navigator.clipboard.writeText(imgDom.title)
        .then(() => {
            message.setOption({
                message: '复制路径成功！',
                type: "success",
                duration: 1000,
            });
            console.log('文本已成功复制到剪贴板');
        })
        .catch(err => {
            console.error('无法复制到剪贴板: ', err);
        });
}

/**
 * 初始化事件
 */
window.addEventListener('pywebviewready', function () {
    featureFileStorageAddress.value = 'pywebview is ready'
    // 加载配置文件
    loadConfiguration()
})

/**
 * 加载配置文件
 */
function loadConfiguration() {
    window.pywebview.api.load_configuration_file().then((response) => {
        featureFileStorageAddress.value = response.feature_path
        searchSimilarImagesNumber.value = response.result_count
        imgFolderPath.value = response.gallery_path
    })
}
