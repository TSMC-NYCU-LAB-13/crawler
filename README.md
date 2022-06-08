# backend

## 部署步驟

- 建立 ns 與 secret
  
    ```sh
    kubectl create -n tsmc-nycu-lab-13 secret generic crawler-env --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -
    ```

- 部署

    ```sh
    kubectl apply -k kustomize-crawler
    ```
