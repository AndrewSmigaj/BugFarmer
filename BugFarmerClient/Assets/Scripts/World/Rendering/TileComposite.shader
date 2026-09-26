Shader "Hidden/BugFarmer/TileComposite"
{
    // M0 shaped-ground render spike: blend two ground material textures through a shape mask into one tile.
    // Runs via a manual Graphics.Blit into a RenderTexture (base tiles are import isReadable:0, so we composite
    // on the GPU, never CPU GetPixels). Mask.r = 1 -> material A, 0 -> material B. Unlit straight copy — the
    // project is Gamma color space (m_ActiveColorSpace: 0), so no sRGB/linear conversion to reconcile.
    Properties
    {
        _MainTex ("Base (unused)", 2D) = "white" {}
        _MatA ("Material A", 2D) = "white" {}
        _MatB ("Material B", 2D) = "white" {}
        _Mask ("Shape Mask", 2D) = "white" {}
    }
    SubShader
    {
        Tags { "RenderType" = "Opaque" }
        Cull Off ZWrite Off ZTest Always

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata { float4 vertex : POSITION; float2 uv : TEXCOORD0; };
            struct v2f     { float4 pos : SV_POSITION; float2 uv : TEXCOORD0; };

            sampler2D _MatA;
            sampler2D _MatB;
            sampler2D _Mask;

            v2f vert (appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                fixed4 a = tex2D(_MatA, i.uv);
                fixed4 b = tex2D(_MatB, i.uv);
                fixed  m = tex2D(_Mask, i.uv).r;
                return lerp(b, a, m);
            }
            ENDCG
        }
    }
}
